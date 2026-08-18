"""Deterministic tool selection. The model does not choose or execute tools."""

from __future__ import annotations

import re

from pixel.domain import Intent, IntentResult, ToolCall
from pixel.tools.catalog import detect_audience, detect_topic
from pixel.tools.types import SourceOffer
from pixel.tools.urls import extract_url

_PROGRAM = re.compile(
    r"\b(programs?|firstline|cyberworks|cyberlaunch|seccdc|cmmc)\b",
    re.I,
)
_RESOURCE = re.compile(
    r"\b(resources? for|educator resources|business resources|events?)\b",
    re.I,
)
_SEARCH = re.compile(r"\bsearch (approved )?content\b", re.I)
_ORDINAL = re.compile(r"\b(first|second|third|1st|2nd|3rd)\b", re.I)
_THAT = re.compile(r"\b(that|this|it|the program|the page|the site)\b", re.I)


def _ordinal_index(text: str) -> int | None:
    key = text.lower()
    if "first" in key or "1st" in key:
        return 0
    if "second" in key or "2nd" in key:
        return 1
    if "third" in key or "3rd" in key:
        return 2
    return None


def resolve_offer(text: str, offers: tuple[SourceOffer, ...]) -> SourceOffer | None:
    if not offers:
        return None
    key = text.lower()
    for offer in offers:
        title = offer.title.lower()
        if title and title in key:
            return offer
        if offer.source_id.replace("cf-", "") in key.replace(" ", ""):
            return offer
    index = _ordinal_index(text)
    if index is not None and index < len(offers):
        return offers[index]
    if _THAT.search(text) and len(offers) == 1:
        return offers[0]
    if _THAT.search(text) and _ordinal_index(text) is None and "open" in key:
        return offers[0]
    return None


def select_tool_calls(
    text: str,
    routing: IntentResult,
    *,
    last_offers: tuple[SourceOffer, ...] = (),
    max_calls: int = 2,
    retrieval_already_ran: bool = False,
) -> tuple[ToolCall, ...]:
    calls: list[ToolCall] = []
    if routing.intent == Intent.navigation:
        url = extract_url(text)
        if url:
            calls.append(ToolCall(name="navigate_to_url", arguments={"url": url}))
        else:
            offer = resolve_offer(text, last_offers)
            if offer is not None:
                calls.append(
                    ToolCall(name="navigate_to_url", arguments={"source_id": offer.source_id})
                )
            elif re.search(r"cyber ?florida", text, re.I):
                calls.append(ToolCall(name="navigate_to_url", arguments={"source_id": "cf-home"}))
        return tuple(calls[: max(1, max_calls)])

    audience = detect_audience(text)
    topic = detect_topic(text)
    if _PROGRAM.search(text) and routing.intent == Intent.cyberflorida_knowledge:
        args = {"keywords": text}
        if audience:
            args["audience"] = audience
        if topic:
            args["topic"] = topic
        calls.append(ToolCall(name="find_program", arguments=args))
    elif _RESOURCE.search(text) and routing.intent == Intent.cyberflorida_knowledge:
        args = {"keywords": text}
        if audience:
            args["audience"] = audience
        if topic:
            args["topic"] = topic
        calls.append(ToolCall(name="find_resource", arguments=args))
    elif _SEARCH.search(text) and not retrieval_already_ran:
        calls.append(ToolCall(name="search_approved_content", arguments={"query": text}))
    return tuple(calls[: max(1, max_calls)])
