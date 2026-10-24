
from app.ai.chunking import build_evidence_chunks
from app.schemas.evidence import EvidenceSource
from app.schemas.incident import Incident, IncidentSeverity
from app.simulators.auth_simulator import generate_auth_failure_logs
from app.simulators.metrics_simulator import (
    generate_auth_failure_metrics,
)


def _incident() -> Incident:
    return Incident(
        title="Authentication service failure",
        description="Users receive 401 errors after deployment",
        severity=IncidentSeverity.HIGH,
    )


def test_build_evidence_chunks_covers_all_sources():
    incident = _incident()
    logs = generate_auth_failure_logs(incident.id)
    metrics = generate_auth_failure_metrics(incident.id)

    chunks = build_evidence_chunks(incident, logs, metrics)

    sources = [chunk.source for chunk in chunks]

    assert sources.count(EvidenceSource.INCIDENT) == 1
    assert sources.count(EvidenceSource.LOG) == 4
    assert sources.count(EvidenceSource.METRIC) == 5
    assert sources.count(EvidenceSource.METRIC_TREND) == 1
    assert all(chunk.incident_id == incident.id for chunk in chunks)


def test_log_chunk_includes_metadata():
    incident = _incident()
    logs = generate_auth_failure_logs(incident.id)

    chunks = build_evidence_chunks(incident, logs, [])
    log_texts = [
        chunk.text
        for chunk in chunks
        if chunk.source == EvidenceSource.LOG
    ]

    assert "Refresh token signature verification failed" in log_texts[1]
    assert "error_code=INVALID_TOKEN_SIGNATURE" in log_texts[1]


def test_metric_trend_summarizes_series():
    incident = _incident()
    metrics = generate_auth_failure_metrics(incident.id)

    chunks = build_evidence_chunks(incident, [], metrics)
    trend = next(
        chunk
        for chunk in chunks
        if chunk.source == EvidenceSource.METRIC_TREND
    )

    assert "changed from 2% to 42%" in trend.text
    assert "5 samples" in trend.text
