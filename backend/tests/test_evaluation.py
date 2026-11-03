
from uuid import uuid4

import pytest

from app.ai.chunking import build_evidence_chunks
from app.evaluation.retrieval import (
    CASES,
    CaseResult,
    RetrievalCase,
    RetrievalReport,
    evaluate_retrieval,
)
from app.schemas.incident import Incident, IncidentScenario
from app.simulators.scenarios import (
    SAMPLE_INCIDENTS,
    generate_logs,
    generate_metrics,
)
from tests.fakes import KeywordEmbedder


def _result(rank):
    case = RetrievalCase(IncidentScenario.AUTH_FAILURE, "question", "text")
    return CaseResult(case=case, rank=rank)


def test_report_metrics():
    report = RetrievalReport(
        k=3,
        results=[_result(1), _result(2), _result(None), _result(3)],
    )

    assert report.hit_rate == pytest.approx(0.75)
    assert report.mrr == pytest.approx((1 + 1 / 2 + 1 / 3) / 4)


def test_empty_report():
    report = RetrievalReport(k=3, results=[])

    assert report.hit_rate == 0.0
    assert report.mrr == 0.0


def test_evaluation_runs_over_all_cases(vector_store):
    report = evaluate_retrieval(KeywordEmbedder(), vector_store, k=3)

    assert len(report.results) == len(CASES)
    assert 0.0 <= report.hit_rate <= 1.0

    signature_case = next(
        result
        for result in report.results
        if "refresh tokens" in result.case.question
    )

    assert signature_case.rank == 1


def test_expected_text_matches_exactly_one_chunk_per_case():
    for case in CASES:
        incident = Incident(
            **SAMPLE_INCIDENTS[case.scenario].model_dump()
        )
        chunks = build_evidence_chunks(
            incident,
            generate_logs(case.scenario, uuid4()),
            generate_metrics(case.scenario, uuid4()),
        )
        matches = [
            chunk
            for chunk in chunks
            if case.expected_text.lower() in chunk.text.lower()
        ]

        assert len(matches) == 1, case.question
