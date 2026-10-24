
import os

from dotenv import load_dotenv


load_dotenv()


def openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY") or None


def openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def openai_embedding_model() -> str:
    return os.getenv(
        "OPENAI_EMBEDDING_MODEL",
        "text-embedding-3-small",
    )
