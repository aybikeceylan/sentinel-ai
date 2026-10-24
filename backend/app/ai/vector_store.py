
import math
from uuid import UUID

from app.schemas.evidence import EvidenceChunk, RetrievedEvidence


class InMemoryVectorStore:
    def __init__(self):
        self._entries: dict[
            UUID, list[tuple[EvidenceChunk, list[float]]]
        ] = {}

    def has_incident(self, incident_id: UUID) -> bool:
        return incident_id in self._entries

    def add(
        self,
        chunks: list[EvidenceChunk],
        vectors: list[list[float]],
    ) -> None:

        if len(chunks) != len(vectors):
            raise ValueError(
                "Each chunk must have exactly one vector"
            )

        for chunk, vector in zip(chunks, vectors):
            self._entries.setdefault(chunk.incident_id, []).append(
                (chunk, vector)
            )

    def search(
        self,
        incident_id: UUID,
        query_vector: list[float],
        top_k: int,
    ) -> list[RetrievedEvidence]:

        scored = [
            RetrievedEvidence(
                chunk=chunk,
                score=cosine_similarity(query_vector, vector),
            )
            for chunk, vector in self._entries.get(incident_id, [])
        ]

        scored.sort(key=lambda item: item.score, reverse=True)

        return scored[:top_k]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vectors must have the same dimension")

    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)
