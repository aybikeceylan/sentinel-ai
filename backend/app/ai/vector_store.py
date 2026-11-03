
import re
from typing import Protocol
from uuid import UUID

from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

from app.schemas.evidence import (
    EvidenceChunk,
    EvidenceSource,
    RetrievedEvidence,
)


class VectorStore(Protocol):
    def has_incident(self, incident_id: UUID) -> bool: ...

    def add(
        self,
        chunks: list[EvidenceChunk],
        vectors: list[list[float]],
    ) -> None: ...

    def search(
        self,
        incident_id: UUID,
        query_vector: list[float],
        top_k: int,
    ) -> list[RetrievedEvidence]: ...


def evidence_collection(
    client: ClientAPI,
    embedding_model: str,
) -> Collection:
    """One collection per embedding model, since vector sizes differ."""

    suffix = re.sub(r"[^a-zA-Z0-9._-]", "-", embedding_model)

    return client.get_or_create_collection(
        name=f"incident-evidence-{suffix}",
        embedding_function=None,
        configuration={"hnsw": {"space": "cosine"}},
    )


class ChromaVectorStore:
    def __init__(self, collection: Collection):
        self.collection = collection

    def has_incident(self, incident_id: UUID) -> bool:
        result = self.collection.get(
            where={"incident_id": str(incident_id)},
            limit=1,
            include=[],
        )
        return bool(result["ids"])

    def add(
        self,
        chunks: list[EvidenceChunk],
        vectors: list[list[float]],
    ) -> None:

        if len(chunks) != len(vectors):
            raise ValueError(
                "Each chunk must have exactly one vector"
            )

        if not chunks:
            return

        self.collection.upsert(
            ids=[str(chunk.id) for chunk in chunks],
            embeddings=vectors,
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "incident_id": str(chunk.incident_id),
                    "source": chunk.source.value,
                }
                for chunk in chunks
            ],
        )

    def search(
        self,
        incident_id: UUID,
        query_vector: list[float],
        top_k: int,
    ) -> list[RetrievedEvidence]:

        result = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where={"incident_id": str(incident_id)},
            include=["documents", "metadatas", "distances"],
        )

        rows = zip(
            result["ids"][0],
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )

        return [
            RetrievedEvidence(
                chunk=EvidenceChunk(
                    id=UUID(chunk_id),
                    incident_id=UUID(str(metadata["incident_id"])),
                    source=EvidenceSource(metadata["source"]),
                    text=document,
                ),
                score=1 - distance,
            )
            for chunk_id, document, metadata, distance in rows
        ]
