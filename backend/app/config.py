
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY") or None


def openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def openai_embedding_model() -> str:
    return os.getenv(
        "OPENAI_EMBEDDING_MODEL",
        "text-embedding-3-small",
    )


def database_path() -> str:
    return os.getenv("SENTINEL_DB_PATH", str(DATA_DIR / "sentinel.db"))


def chroma_path() -> str:
    return os.getenv("CHROMA_PATH", str(DATA_DIR / "chroma"))
