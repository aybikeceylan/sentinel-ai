
from uuid import uuid4

import pytest

from app.ai.vector_store import InMemoryVectorStore, cosine_similarity
from app.schemas.evidence import EvidenceChunk, EvidenceSource


def _chunk(incident_id, text):
    return EvidenceChunk(
        incident_id=incident_id,
        source=EvidenceSource.LOG,
        text=text,
    )


def test_cosine_similarity():
    assert cosine_similarity([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)
    assert cosine_similarity([0, 0], [1, 1]) == 0.0


def test_search_ranks_by_similarity_and_respects_top_k():
    incident_id = uuid4()
    store = InMemoryVectorStore()

    store.add(
        [
            _chunk(incident_id, "far"),
            _chunk(incident_id, "close"),
            _chunk(incident_id, "middle"),
        ],
        [[0.0, 1.0], [1.0, 0.0], [1.0, 1.0]],
    )

    results = store.search(incident_id, [1.0, 0.0], top_k=2)

    assert [item.chunk.text for item in results] == ["close", "middle"]
    assert results[0].score > results[1].score


def test_search_is_scoped_to_incident():
    store = InMemoryVectorStore()
    first, second = uuid4(), uuid4()

    store.add([_chunk(first, "first incident")], [[1.0, 0.0]])

    assert store.has_incident(first)
    assert not store.has_incident(second)
    assert store.search(second, [1.0, 0.0], top_k=5) == []


def test_add_rejects_mismatched_lengths():
    store = InMemoryVectorStore()

    with pytest.raises(ValueError):
        store.add([_chunk(uuid4(), "text")], [])
