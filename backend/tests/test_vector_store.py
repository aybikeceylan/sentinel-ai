
from uuid import uuid4

import pytest

from app.schemas.evidence import EvidenceChunk, EvidenceSource


def _chunk(incident_id, text, source=EvidenceSource.LOG):
    return EvidenceChunk(
        incident_id=incident_id,
        source=source,
        text=text,
    )


def test_search_ranks_by_similarity_and_respects_top_k(vector_store):
    incident_id = uuid4()

    vector_store.add(
        [
            _chunk(incident_id, "far"),
            _chunk(incident_id, "close"),
            _chunk(incident_id, "middle"),
        ],
        [[0.0, 1.0], [1.0, 0.0], [1.0, 1.0]],
    )

    results = vector_store.search(incident_id, [1.0, 0.0], top_k=2)

    assert [item.chunk.text for item in results] == ["close", "middle"]
    assert results[0].score == pytest.approx(1.0)
    assert results[0].score > results[1].score


def test_search_round_trips_chunk_fields(vector_store):
    incident_id = uuid4()
    chunk = _chunk(incident_id, "trend", EvidenceSource.METRIC_TREND)

    vector_store.add([chunk], [[1.0, 0.0]])

    [result] = vector_store.search(incident_id, [1.0, 0.0], top_k=5)

    assert result.chunk == chunk


def test_search_is_scoped_to_incident(vector_store):
    first, second = uuid4(), uuid4()

    vector_store.add([_chunk(first, "first incident")], [[1.0, 0.0]])

    assert vector_store.has_incident(first)
    assert not vector_store.has_incident(second)
    assert vector_store.search(second, [1.0, 0.0], top_k=5) == []


def test_add_is_idempotent_for_same_chunk_ids(vector_store):
    incident_id = uuid4()
    chunk = _chunk(incident_id, "same chunk")

    vector_store.add([chunk], [[1.0, 0.0]])
    vector_store.add([chunk], [[1.0, 0.0]])

    results = vector_store.search(incident_id, [1.0, 0.0], top_k=5)

    assert len(results) == 1


def test_add_rejects_mismatched_lengths(vector_store):
    with pytest.raises(ValueError):
        vector_store.add([_chunk(uuid4(), "text")], [])
