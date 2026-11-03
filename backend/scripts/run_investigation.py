"""Run one real RAG investigation against OpenAI.

Usage (from the backend directory):
    python -m scripts.run_investigation
    python -m scripts.run_investigation --scenario cache_outage
    python -m scripts.run_investigation "Why are refresh tokens rejected?"
"""

import argparse
import json

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.incident import IncidentScenario
from app.simulators.scenarios import SAMPLE_INCIDENTS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?")
    parser.add_argument(
        "--scenario",
        choices=[scenario.value for scenario in IncidentScenario],
        default=IncidentScenario.AUTH_FAILURE.value,
    )
    args = parser.parse_args()

    client = TestClient(app)
    sample = SAMPLE_INCIDENTS[IncidentScenario(args.scenario)]

    incident = client.post(
        "/api/v1/incidents",
        json=sample.model_dump(mode="json"),
    ).json()

    body = {"question": args.question} if args.question else None

    response = client.post(
        f"/api/v1/incidents/{incident['id']}/investigate",
        json=body,
    )

    print(f"HTTP {response.status_code}")
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()
