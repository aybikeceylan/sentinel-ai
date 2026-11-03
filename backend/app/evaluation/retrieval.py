
from dataclasses import dataclass

from app.ai.chunking import build_evidence_chunks
from app.ai.embeddings import Embedder
from app.ai.vector_store import VectorStore
from app.schemas.incident import Incident, IncidentScenario
from app.simulators.scenarios import (
    SAMPLE_INCIDENTS,
    generate_logs,
    generate_metrics,
)


@dataclass(frozen=True)
class RetrievalCase:
    scenario: IncidentScenario
    question: str
    expected_text: str
    """Text that only the relevant evidence chunk contains."""


@dataclass(frozen=True)
class CaseResult:
    case: RetrievalCase
    rank: int | None
    """1-based rank of the first relevant chunk, None if not retrieved."""


@dataclass(frozen=True)
class RetrievalReport:
    k: int
    results: list[CaseResult]

    @property
    def hit_rate(self) -> float:
        if not self.results:
            return 0.0

        hits = sum(1 for result in self.results if result.rank is not None)
        return hits / len(self.results)

    @property
    def mrr(self) -> float:
        if not self.results:
            return 0.0

        return sum(
            1 / result.rank
            for result in self.results
            if result.rank is not None
        ) / len(self.results)


CASES = [
    RetrievalCase(
        IncidentScenario.AUTH_FAILURE,
        "Why are refresh tokens being rejected?",
        "signature verification failed",
    ),
    RetrievalCase(
        IncidentScenario.AUTH_FAILURE,
        "Was there a deployment right before the failures?",
        "Deployment completed: auth-service",
    ),
    RetrievalCase(
        IncidentScenario.AUTH_FAILURE,
        "How many users are affected?",
        "affected_users",
    ),
    RetrievalCase(
        IncidentScenario.DATABASE_POOL_EXHAUSTION,
        "Why are order requests timing out?",
        "Timed out acquiring database connection",
    ),
    RetrievalCase(
        IncidentScenario.DATABASE_POOL_EXHAUSTION,
        "What changed in the order-service configuration?",
        "worker concurrency increased",
    ),
    RetrievalCase(
        IncidentScenario.DATABASE_POOL_EXHAUSTION,
        "Is the Postgres server itself out of connections?",
        "max_connections",
    ),
    RetrievalCase(
        IncidentScenario.CACHE_OUTAGE,
        "What happened to the Redis cluster?",
        "removed from cluster",
    ),
    RetrievalCase(
        IncidentScenario.CACHE_OUTAGE,
        "Why is the catalog database receiving more traffic?",
        "falling back to database",
    ),
    RetrievalCase(
        IncidentScenario.CACHE_OUTAGE,
        "How much did database request volume grow?",
        "request_count changed from",
    ),
]


def index_sample_incidents(
    embedder: Embedder,
    vector_store: VectorStore,
    scenarios: set[IncidentScenario],
) -> dict[IncidentScenario, Incident]:

    incidents = {}

    for scenario in scenarios:
        incident = Incident(**SAMPLE_INCIDENTS[scenario].model_dump())
        chunks = build_evidence_chunks(
            incident,
            generate_logs(scenario, incident.id),
            generate_metrics(scenario, incident.id),
        )

        vector_store.add(
            chunks,
            embedder.embed([chunk.text for chunk in chunks]),
        )
        incidents[scenario] = incident

    return incidents


def evaluate_retrieval(
    embedder: Embedder,
    vector_store: VectorStore,
    cases: list[RetrievalCase] = CASES,
    k: int = 3,
) -> RetrievalReport:

    incidents = index_sample_incidents(
        embedder,
        vector_store,
        {case.scenario for case in cases},
    )

    query_vectors = embedder.embed([case.question for case in cases])
    results = []

    for case, query_vector in zip(cases, query_vectors):
        retrieved = vector_store.search(
            incidents[case.scenario].id,
            query_vector,
            k,
        )

        rank = next(
            (
                position
                for position, item in enumerate(retrieved, start=1)
                if case.expected_text.lower() in item.chunk.text.lower()
            ),
            None,
        )

        results.append(CaseResult(case=case, rank=rank))

    return RetrievalReport(k=k, results=results)
