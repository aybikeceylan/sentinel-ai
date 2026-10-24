
from collections import defaultdict
from datetime import datetime

from app.schemas.evidence import EvidenceChunk, EvidenceSource
from app.schemas.incident import Incident
from app.schemas.log import IncidentLog
from app.schemas.metric import IncidentMetric


def build_evidence_chunks(
    incident: Incident,
    logs: list[IncidentLog],
    metrics: list[IncidentMetric],
) -> list[EvidenceChunk]:

    chunks = [_incident_chunk(incident)]
    chunks.extend(_log_chunk(incident, log) for log in logs)
    chunks.extend(
        _metric_chunk(incident, metric) for metric in metrics
    )
    chunks.extend(_metric_trend_chunks(incident, metrics))

    return chunks


def _incident_chunk(incident: Incident) -> EvidenceChunk:
    return EvidenceChunk(
        incident_id=incident.id,
        source=EvidenceSource.INCIDENT,
        text=(
            f"Incident reported: {incident.title}. "
            f"Severity: {incident.severity.value}. "
            f"Description: {incident.description}"
        ),
    )


def _log_chunk(
    incident: Incident,
    log: IncidentLog,
) -> EvidenceChunk:

    text = (
        f"[{_format_time(log.timestamp)}] {log.service} "
        f"{log.level.value.upper()}: {log.message}"
    )

    if log.metadata:
        details = ", ".join(
            f"{key}={value}" for key, value in log.metadata.items()
        )
        text = f"{text} ({details})"

    return EvidenceChunk(
        incident_id=incident.id,
        source=EvidenceSource.LOG,
        text=text,
    )


def _metric_chunk(
    incident: Incident,
    metric: IncidentMetric,
) -> EvidenceChunk:

    return EvidenceChunk(
        incident_id=incident.id,
        source=EvidenceSource.METRIC,
        text=(
            f"[{_format_time(metric.timestamp)}] {metric.service} "
            f"{metric.metric_type.value} = "
            f"{_format_value(metric.value, metric.unit)}"
        ),
    )


def _metric_trend_chunks(
    incident: Incident,
    metrics: list[IncidentMetric],
) -> list[EvidenceChunk]:

    series: dict[tuple[str, str], list[IncidentMetric]] = defaultdict(list)

    for metric in metrics:
        series[(metric.service, metric.metric_type.value)].append(metric)

    chunks = []

    for (service, metric_type), points in series.items():
        points = sorted(points, key=lambda point: point.timestamp)
        first, last = points[0], points[-1]
        peak = max(points, key=lambda point: point.value)
        unit = first.unit

        chunks.append(
            EvidenceChunk(
                incident_id=incident.id,
                source=EvidenceSource.METRIC_TREND,
                text=(
                    f"{service} {metric_type} changed from "
                    f"{_format_value(first.value, unit)} to "
                    f"{_format_value(last.value, unit)} between "
                    f"{_format_time(first.timestamp)} and "
                    f"{_format_time(last.timestamp)} "
                    f"({len(points)} samples, peak "
                    f"{_format_value(peak.value, unit)})"
                ),
            )
        )

    return chunks


def _format_time(timestamp: datetime) -> str:
    return timestamp.isoformat(timespec="seconds")


def _format_value(value: float, unit: str) -> str:
    if unit == "ratio":
        return f"{value:.0%}"

    return f"{value:g} {unit}"
