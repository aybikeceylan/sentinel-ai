"""Run one real RAG investigation against OpenAI.

Usage (from the backend directory):
    python -m scripts.run_investigation
    python -m scripts.run_investigation "Why are refresh tokens rejected?"
"""

import json
import sys

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    client = TestClient(app)

    incident = client.post(
        "/api/v1/incidents",
        json={
            "title": "Authentication service failure",
            "description": "Users receive 401 errors after deployment",
            "severity": "high",
        },
    ).json()

    body = {"question": sys.argv[1]} if len(sys.argv) > 1 else None

    response = client.post(
        f"/api/v1/incidents/{incident['id']}/investigate",
        json=body,
    )

    print(f"HTTP {response.status_code}")
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()
