
from app.schemas.investigation import (
    ConfidenceLevel,
    InvestigationResult,
)


VOCABULARY = [
    "deployment",
    "version",
    "token",
    "signature",
    "401",
    "unauthorized",
    "users",
    "error_rate",
    "threshold",
    "latency",
]


class KeywordEmbedder:
    """Deterministic embedder that counts vocabulary words."""

    def __init__(self):
        self.calls: list[list[str]] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(list(texts))

        return [
            [float(text.lower().count(word)) for word in VOCABULARY]
            for text in texts
        ]


class FakeAnalyzer:
    model = "fake-llm"

    def __init__(self):
        self.prompts: list[str] = []

    def analyze(self, incident_data: str) -> InvestigationResult:
        self.prompts.append(incident_data)

        return InvestigationResult(
            summary="Auth failures started after a deployment.",
            probable_root_cause="auth-service v2.4.0 token signing change",
            confidence=ConfidenceLevel.MEDIUM,
            evidence=["[E1]"],
            recommended_actions=["Roll back auth-service to v2.3.x"],
        )
