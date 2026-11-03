"""Measure retrieval quality with real OpenAI embeddings.

Uses an in-memory Chroma collection, so the persistent index is untouched.

Usage (from the backend directory):
    python -m scripts.evaluate_retrieval
    python -m scripts.evaluate_retrieval --k 1
"""

import argparse
import sys

import chromadb
from chromadb.config import Settings
from openai import OpenAI, OpenAIError

from app import config
from app.ai.embeddings import OpenAIEmbedder
from app.ai.vector_store import ChromaVectorStore, evidence_collection
from app.evaluation.retrieval import evaluate_retrieval


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()

    api_key = config.openai_api_key()

    if api_key is None:
        sys.exit("OPENAI_API_KEY is not configured")

    embedding_model = config.openai_embedding_model()
    chroma_client = chromadb.EphemeralClient(
        settings=Settings(anonymized_telemetry=False)
    )

    try:
        report = evaluate_retrieval(
            OpenAIEmbedder(OpenAI(api_key=api_key), embedding_model),
            ChromaVectorStore(
                evidence_collection(
                    chroma_client,
                    f"eval-{embedding_model}",
                )
            ),
            k=args.k,
        )
    except OpenAIError as error:
        sys.exit(f"OpenAI request failed: {error}")

    for result in report.results:
        rank = result.rank if result.rank is not None else "miss"
        print(
            f"{str(rank):>4}  {result.case.scenario.value:<26} "
            f"{result.case.question}"
        )

    print()
    print(f"embedding model: {embedding_model}")
    print(f"hit rate@{report.k}: {report.hit_rate:.2f}")
    print(f"MRR@{report.k}:      {report.mrr:.2f}")


if __name__ == "__main__":
    main()
