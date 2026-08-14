"""Measure retrieval, groundedness, citations, abstention, and freshness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pixel.knowledge.registry import get_source_by_id
from pixel.knowledge.retrieve import KnowledgeRetriever
from pixel.knowledge.runtime import fixture_retriever
from pixel.orchestrator.fallbacks import ORG_ABSTAIN
from pixel.orchestrator.process import OrchestratorConfig, process_turn
from pixel.providers.mock import MockLLM, MockTextToSpeech
from pixel.shared.cancellation import CancellationFlag

_ABSTAIN_MARKERS = (
    "cannot verify",
    "will not guess",
    "not published",
    "cannot confirm",
    "not listed",
    "do not guess",
    "must not invent",
    "not invent",
)


def load_cases(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def default_cases_path() -> Path:
    return Path(__file__).resolve().parents[4] / "evals" / "knowledge" / "cases.jsonl"


def _hit_at(chunks: tuple, expected_source: str, k: int) -> bool:
    if not expected_source:
        return False
    return any(chunk.source_id == expected_source for chunk in chunks[:k])


def _looks_like_abstain(text: str) -> bool:
    lowered = text.lower()
    if any(marker in lowered for marker in _ABSTAIN_MARKERS):
        return True
    return ORG_ABSTAIN[:24].lower() in lowered


def _source_url(source_id: str) -> str:
    source = get_source_by_id(source_id)
    return source.canonical_url.rstrip("/") if source else ""


def _grounded(answer: str, chunks: tuple) -> bool:
    if _looks_like_abstain(answer):
        return True
    blob = " ".join(chunk.content.lower() for chunk in chunks)
    tokens = [token.strip(".,") for token in answer.lower().split() if len(token) > 4]
    if not tokens or not blob:
        return False
    overlap = sum(1 for token in tokens if token in blob)
    return overlap / max(1, len(tokens)) >= 0.2


def evaluate(
    cases: list[dict[str, Any]],
    *,
    retriever: KnowledgeRetriever | None = None,
) -> dict[str, Any]:
    active = retriever or fixture_retriever()
    retrieval_cases = [
        case
        for case in cases
        if case.get("expected_source") and not case.get("expected_abstention")
    ]
    hit1 = hit3 = hit5 = 0
    precise = 0
    precise_denom = 0
    grounded = 0
    correct = 0
    cited = 0
    answer_n = 0
    abstain_ok = 0
    abstain_n = 0
    fresh_ok = 0
    fresh_n = 0
    latencies: list[int] = []
    llm = MockLLM()
    tts = MockTextToSpeech()
    config = OrchestratorConfig(max_attempts=1, backoff_seconds=0)

    for case in cases:
        question = str(case["question"])
        expected = str(case.get("expected_source") or "")
        hits = active.retrieve(question)
        latencies.append(hits.latency_ms)
        if expected and not case.get("expected_abstention"):
            hit1 += int(_hit_at(hits.chunks, expected, 1))
            hit3 += int(_hit_at(hits.chunks, expected, 3))
            hit5 += int(_hit_at(hits.chunks, expected, 5))
            if hits.chunks:
                precise_denom += len(hits.chunks)
                precise += sum(1 for chunk in hits.chunks if chunk.source_id == expected)

        outcome = process_turn(
            text=question,
            llm=llm,
            tts=tts,
            cancellation=CancellationFlag(),
            speak=False,
            config=config,
            retriever=active,
        )
        answer = outcome.response.text
        urls = {item.url.rstrip("/") for item in outcome.response.sources}

        if case.get("expected_abstention"):
            abstain_n += 1
            abstain_ok += int(_looks_like_abstain(answer) or not hits.available)
        else:
            answer_n += 1
            is_grounded = _grounded(answer, hits.chunks)
            grounded += int(is_grounded)
            expected_behavior = str(case.get("expected_behavior") or "").lower()
            if expected_behavior:
                correct += int(expected_behavior in answer.lower() and is_grounded)
            else:
                correct += int(is_grounded)
            if expected and _source_url(expected) in urls:
                cited += 1

        if case.get("requires_current_information"):
            fresh_n += 1
            if case.get("expected_abstention"):
                fresh_ok += int(_looks_like_abstain(answer) or not hits.available)
            elif expected:
                fresh_ok += int(_hit_at(hits.chunks, expected, 3))

    retrieval_n = max(1, len(retrieval_cases))
    latencies.sort()
    p50 = latencies[len(latencies) // 2] if latencies else None
    p95_index = min(len(latencies) - 1, int(len(latencies) * 0.95)) if latencies else 0
    p95 = latencies[p95_index] if latencies else None
    return {
        "total": len(cases),
        "hit_at_1": hit1 / retrieval_n,
        "hit_at_3": hit3 / retrieval_n,
        "hit_at_5": hit5 / retrieval_n,
        "context_precision": (precise / precise_denom) if precise_denom else 0.0,
        "groundedness": grounded / max(1, answer_n),
        "answer_correctness": correct / max(1, answer_n),
        "citation_correctness": cited / retrieval_n,
        "abstention": (abstain_ok / abstain_n) if abstain_n else 1.0,
        "freshness": (fresh_ok / fresh_n) if fresh_n else 1.0,
        "retrieval_latency_p50_ms": p50,
        "retrieval_latency_p95_ms": p95,
        "retrieval_case_count": len(retrieval_cases),
        "abstention_case_count": abstain_n,
    }
