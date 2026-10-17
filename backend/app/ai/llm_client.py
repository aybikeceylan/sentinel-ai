
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.investigation import InvestigationResult


load_dotenv()


class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"]
        )

        self.model = os.getenv(
            "OPENAI_MODEL",
            "gpt-4.1-mini",
        )

    def analyze(
        self,
        incident_data: str,
    ) -> InvestigationResult:

        response = self.client.responses.parse(
            model=self.model,
            instructions=(
                "You are a production incident investigator. "
                "Analyze only the provided evidence. "
                "Do not invent logs, metrics, or facts. "
                "Distinguish hypotheses from confirmed causes. "
                "Return a structured investigation result."
            ),
            input=incident_data,
            text_format=InvestigationResult,
        )

        result = response.output_parsed

        if result is None:
            raise ValueError(
                "LLM did not return a structured investigation"
            )

        return result
