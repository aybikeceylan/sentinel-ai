
import pytest
from fastapi.testclient import TestClient

from app import dependencies
from app.ai.vector_store import InMemoryVectorStore
from app.main import app
from app.services.investigation_service import InvestigationService
from tests.fakes import FakeAnalyzer, KeywordEmbedder


client = TestClient(app)


@pytest.fixture
def fakes():
    embedder = KeywordEmbedder()
    analyzer = FakeAnalyzer()

    service = InvestigationService(
        incident_service=dependencies.incident_service,
        evidence_service=dependencies.evidence_service,
        embedder=embedder,
        vector_store=InMemoryVectorStore(),
        analyzer=analyzer,
        repository=dependencies.investigation_repository,
    )

    app.dependency_overrides[
        dependencies.get_investigation_service
    ] = lambda: service

    yield embedder, analyzer

    app.dependency_overrides.clear()


def _create_incident() -> str:
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Authentication service failure",
            "description": "Users receive 401 errors after deployment",
            "severity": "high",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_investigate_retrieves_relevant_evidence(fakes):
    embedder, analyzer = fakes
    incident_id = _create_incident()

    response = client.post(
        f"/api/v1/incidents/{incident_id}/investigate",
        json={
            "question": "Why does token signature verification fail?",
            "top_k": 3,
        },
    )

    assert response.status_code == 201

    report = response.json()

    assert report["incident_id"] == incident_id
    assert report["model"] == "fake-llm"
    assert report["result"]["confidence"] == "medium"
    assert len(report["retrieved_evidence"]) == 3

    top_chunk = report["retrieved_evidence"][0]["chunk"]

    assert "signature" in top_chunk["text"]

    prompt = analyzer.prompts[-1]

    assert "Why does token signature verification fail?" in prompt
    assert "[E1]" in prompt
    assert "[E3]" in prompt
    assert "[E4]" not in prompt


def test_investigate_without_body_uses_default_question(fakes):
    incident_id = _create_incident()

    response = client.post(
        f"/api/v1/incidents/{incident_id}/investigate"
    )

    assert response.status_code == 201
    assert "root cause" in response.json()["question"]
    assert len(response.json()["retrieved_evidence"]) == 6


def test_investigate_indexes_evidence_once(fakes):
    embedder, _ = fakes
    incident_id = _create_incident()

    for _ in range(2):
        response = client.post(
            f"/api/v1/incidents/{incident_id}/investigate"
        )
        assert response.status_code == 201

    batch_sizes = [len(call) for call in embedder.calls]

    assert batch_sizes == [11, 1, 1]


def test_investigation_updates_status_and_history(fakes):
    incident_id = _create_incident()

    client.post(f"/api/v1/incidents/{incident_id}/investigate")

    incident = client.get(f"/api/v1/incidents/{incident_id}").json()

    assert incident["status"] == "investigating"

    history = client.get(
        f"/api/v1/incidents/{incident_id}/investigations"
    )

    assert history.status_code == 200
    assert len(history.json()) == 1


def test_investigate_unknown_incident(fakes):
    response = client.post(
        "/api/v1/incidents/"
        "00000000-0000-0000-0000-000000000000/investigate"
    )

    assert response.status_code == 404


def test_investigate_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    dependencies.get_investigation_service.cache_clear()

    incident_id = _create_incident()

    response = client.post(
        f"/api/v1/incidents/{incident_id}/investigate"
    )

    assert response.status_code == 503

    dependencies.get_investigation_service.cache_clear()
