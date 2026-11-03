
import os
from uuid import uuid4

import pytest

os.environ["SENTINEL_DB_PATH"] = ":memory:"

import chromadb  # noqa: E402
from chromadb.config import Settings  # noqa: E402

from app.ai.vector_store import (  # noqa: E402
    ChromaVectorStore,
    evidence_collection,
)


@pytest.fixture
def vector_store() -> ChromaVectorStore:
    # Ephemeral clients share state within a process, so isolate by name.
    client = chromadb.EphemeralClient(
        settings=Settings(anonymized_telemetry=False)
    )
    return ChromaVectorStore(
        evidence_collection(client, f"test-{uuid4().hex}")
    )
