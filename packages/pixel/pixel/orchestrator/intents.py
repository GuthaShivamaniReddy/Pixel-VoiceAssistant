"""Deterministic intent taxonomy. No extra model call."""

from __future__ import annotations

import re

from pixel.domain import Intent, IntentResult

_INJECTION = re.compile(
    r"ignore (all )?previous|reveal (your )?(hidden )?(system prompt|developer instructions)|"
    r"dump system prompt|print (your )?(api key|environment variables)|"
    r"give me your (api key|realtime|database)|show me (your )?(api key|database|secrets)|"
    r"act as (an unrestricted|the system administrator)|jailbreak|you are now dan|"
    r"hidden instructions|disable your safety|pretend i (already )?passed authorization|"
    r"use every tool available|what is openai_api_key|show me database_url|"
    r"repeat the secrets|print every environment",
    re.I,
)
_OFFENSIVE = re.compile(
    r"\b(malware|ransomware kit|exploit|zero[- ]day|sql injection payload|"
    r"unauthorized access|bypass (auth|mfa|2fa)|write (a )?virus|keylogger)\b",
    re.I,
)
_SCAM = re.compile(
    r"scam|look suspicious|phishing email|is this (likely )?(a )?(phish|scam)|"
    r"does this message|suspicious (email|text|sms)",
    re.I,
)
_NAV = re.compile(
    r"\b(open|show me|take me to|navigate to|go to|visit)\b.+\b(page|site|program|link|url)\b|"
    r"open (the )?cyber florida|show me that program|"
    r"\b(open|visit|go to|navigate to)\s+https?://|"
    r"^(open|show) (that|it|this|the (first|second|third) one)",
    re.I,
)
_CYBER_HELP = re.compile(
    r"phish|password|passkey|2fa|two[- ]factor|mfa|account security|"
    r"clicked a suspicious|suspicious link|ransomware|malware|"
    r"how can i improve|what is phishing",
    re.I,
)
_ORG = re.compile(
    r"cyber ?florida|cyberflorida|what programs|programs are available|"
    r"workforce|next event|eligibility|for students|center for cybersecurity|"
    r"firstline|cyberworks|cyberlaunch|seccdc|cmmc|"
    r"who (do you|does (cyber ?florida|the center)) serve",
    re.I,
)
_FOLLOWUP = re.compile(
    r"^(tell me more\b.*|"
    r"what about( that| it| them| beginners| eligibility)?|"
    r"that one|the first one|the second one|the third one|"
    r"and (the|that)|eligibility( requirements)?)[\s.?!]*$",
    re.I,
)
_GREETING = re.compile(
    r"^(hi|hello|hey|help|what can you do|who are you|what are you)[\s.?!]*$",
    re.I,
)


def _result(
    intent: Intent,
    *,
    confidence: float,
    reason: str,
    requires_retrieval: bool = False,
    requires_tool: bool = False,
    skip_model: bool = False,
) -> IntentResult:
    if confidence < 0 or confidence > 1:
        raise ValueError("intent confidence must be between 0 and 1")
    return IntentResult(
        intent=intent,
        confidence=confidence,
        reason=reason,
        requires_retrieval=requires_retrieval,
        requires_tool=requires_tool,
        skip_model=skip_model,
    )


def classify_intent(text: str, *, last_intent: Intent | None = None) -> IntentResult:
    key = " ".join(text.lower().split()).strip()
    if not key:
        return _result(Intent.clarification, confidence=1.0, reason="empty", skip_model=True)

    if _INJECTION.search(key):
        return _result(
            Intent.unsupported, confidence=0.99, reason="prompt_injection", skip_model=True
        )
    if _OFFENSIVE.search(key):
        return _result(
            Intent.unsupported, confidence=0.95, reason="offensive_or_unsafe", skip_model=True
        )
    if _SCAM.search(key):
        return _result(Intent.scam_help, confidence=0.9, reason="scam_indicators")
    if _NAV.search(key):
        return _result(
            Intent.navigation,
            confidence=0.88,
            reason="navigation_request",
            requires_tool=True,
            skip_model=True,
        )
    if _CYBER_HELP.search(key):
        return _result(Intent.cybersecurity_help, confidence=0.9, reason="defensive_help")
    if _ORG.search(key):
        return _result(
            Intent.cyberflorida_knowledge,
            confidence=0.9,
            reason="org_question",
            requires_retrieval=True,
        )
    if _FOLLOWUP.match(key):
        prior = last_intent
        if prior in {
            Intent.cyberflorida_knowledge,
            Intent.cybersecurity_help,
            Intent.scam_help,
            Intent.navigation,
        }:
            assert prior is not None
            return _result(
                prior,
                confidence=0.8,
                reason="follow_up",
                requires_retrieval=prior == Intent.cyberflorida_knowledge,
                requires_tool=prior == Intent.navigation,
            )
        return _result(
            Intent.clarification,
            confidence=0.85,
            reason="follow_up_no_referent",
            skip_model=True,
        )
    if _GREETING.match(key):
        return _result(Intent.clarification, confidence=0.8, reason="greeting")
    return _result(Intent.unsupported, confidence=0.55, reason="out_of_scope")


def validate_intent_result(result: IntentResult) -> IntentResult:
    Intent(result.intent)
    if not 0 <= result.confidence <= 1:
        return _result(Intent.unsupported, confidence=0.0, reason="invalid_structured_output")
    if result.requires_tool and result.intent not in {Intent.navigation}:
        return _result(result.intent, confidence=result.confidence, reason=result.reason)
    return result
