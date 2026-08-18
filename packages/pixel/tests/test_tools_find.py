from dataclasses import replace

from pixel.knowledge.registry import PUBLIC_SOURCES
from pixel.shared.cancellation import CancellationFlag
from pixel.tools.catalog import list_sources
from pixel.tools.handlers import find_program, find_resource, search_approved_content
from pixel.tools.registry import production_registry
from pixel.tools.runner import execute_tool
from pixel.tools.types import AuthContext, ConfirmationState


def test_find_program_students() -> None:
    result = find_program({"audience": "students", "keywords": "programs for students"})
    assert result.ok is True
    assert result.actions
    hrefs = [action.href for action in result.actions]
    assert any("seccdc" in href for href in hrefs)
    assert any("cyberworks" in href for href in hrefs)
    assert all("cmmc" not in href for href in hrefs)
    assert all("cyberlaunch" not in href for href in hrefs)
    assert all("firstline" not in href for href in hrefs)


def test_find_program_no_match() -> None:
    result = find_program({"audience": "business", "topic": "collegiate"})
    assert result.status == "not_found"
    assert result.actions == ()


def test_find_program_malformed_audience_rejected() -> None:
    outcome = execute_tool(
        "find_program",
        {"audience": "not-a-real-audience"},
        registry=production_registry(),
        auth=AuthContext(),
        confirmation=ConfirmationState(),
        cancellation=CancellationFlag(),
        timeout_seconds=2,
    )
    assert outcome.status == "invalid_input"


def test_find_resource_educators() -> None:
    result = find_resource({"audience": "educators"})
    assert result.ok is True
    assert any("cyberlaunch" in action.href for action in result.actions)


def test_inactive_source_not_listed() -> None:
    inactive = tuple(
        replace(item, active=False) if item.id == "cf-seccdc" else item for item in PUBLIC_SOURCES
    )
    found = list_sources(programs_only=True, audience="students", sources=inactive)
    assert all(item.id != "cf-seccdc" for item in found)


def test_search_approved_content_hits_active_corpus() -> None:
    result = search_approved_content({"query": "What is FirstLine at Cyber Florida?"})
    assert result.ok is True
    assert result.sources


def test_search_requires_query() -> None:
    outcome = execute_tool(
        "search_approved_content",
        {},
        registry=production_registry(),
        auth=AuthContext(),
        confirmation=ConfirmationState(),
        cancellation=CancellationFlag(),
        timeout_seconds=2,
    )
    assert outcome.status == "invalid_input"


def test_extra_and_wrong_type_and_oversized_rejected() -> None:
    registry = production_registry()
    extra = execute_tool(
        "find_program",
        {"audience": "students", "shell": "rm"},
        registry=registry,
        auth=AuthContext(),
        confirmation=ConfirmationState(),
        cancellation=CancellationFlag(),
        timeout_seconds=2,
    )
    assert extra.status == "invalid_input"
    wrong = execute_tool(
        "find_program",
        {"audience": 1},  # type: ignore[dict-item]
        registry=registry,
        auth=AuthContext(),
        confirmation=ConfirmationState(),
        cancellation=CancellationFlag(),
        timeout_seconds=2,
    )
    assert wrong.status == "invalid_input"
    huge = execute_tool(
        "find_program",
        {"keywords": "x" * 500},
        registry=registry,
        auth=AuthContext(),
        confirmation=ConfirmationState(),
        cancellation=CancellationFlag(),
        timeout_seconds=2,
    )
    assert huge.status == "invalid_input"
    nullish = execute_tool(
        "find_program",
        {"audience": None},  # type: ignore[dict-item]
        registry=registry,
        auth=AuthContext(),
        confirmation=ConfirmationState(),
        cancellation=CancellationFlag(),
        timeout_seconds=2,
    )
    assert nullish.status == "invalid_input"
