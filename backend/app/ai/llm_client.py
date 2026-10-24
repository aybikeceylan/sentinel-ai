
from typing import Protocol

from openai import OpenAI

from app.schemas.investigation import InvestigationResult


INSTRUCTIONS = (
    "You are a production incident investigator. "
    "Analyze only the provided evidence. "
    "Do not invent logs, metrics, or facts. "
    "Distinguish hypotheses from confirmed causes. "
    "If the evidence is insufficient, say so and use low confidence. "
    "Return a structured investigation result."
)


class IncidentAnalyzer(Protocol):
    model: str

    def analyze(self, incident_data: str) -> InvestigationResult: ...


class LLMClient:
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def analyze(
        self,
        incident_data: str,
    ) -> InvestigationResult:

        response = self.client.responses.parse(
            model=self.model,
            instructions=INSTRUCTIONS,
            input=incident_data,
            text_format=InvestigationResult,
        )

        result = response.output_parsed

        if result is None:
            raise ValueError(
                "LLM did not return a structured investigation"
            )

        return result
