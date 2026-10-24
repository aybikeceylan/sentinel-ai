
from app.schemas.evidence import RetrievedEvidence
from app.schemas.incident import Incident


def build_investigation_prompt(
    incident: Incident,
    question: str,
    evidence: list[RetrievedEvidence],
) -> str:

    lines = [
        "Incident",
        f"Title: {incident.title}",
        f"Severity: {incident.severity.value}",
        f"Status: {incident.status.value}",
        f"Description: {incident.description}",
        "",
        "Question",
        question,
        "",
        "Retrieved evidence (most relevant first)",
    ]

    if evidence:
        lines.extend(
            f"[E{index}] ({item.chunk.source.value}) {item.chunk.text}"
            for index, item in enumerate(evidence, start=1)
        )
    else:
        lines.append("No evidence was retrieved.")

    lines.extend(
        [
            "",
            "Answer the question using only the evidence above. "
            "Reference evidence ids such as [E1] in the evidence list.",
        ]
    )

    return "\n".join(lines)
