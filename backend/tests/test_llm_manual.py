
from app.ai.llm_client import LLMClient


client = LLMClient()

result = client.analyze(
    """
    Incident: Authentication failure

    Logs:
    - Deployment completed: auth-service v2.4.0
    - Refresh token signature verification failed
    - Multiple users receiving 401 Unauthorized

    Metrics:
    - Authentication error rate increased from 2% to 42%

    Investigate the likely cause.
    """
)

print(result.model_dump_json(indent=2))
