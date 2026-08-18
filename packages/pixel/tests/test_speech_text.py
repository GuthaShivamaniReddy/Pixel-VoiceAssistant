from __future__ import annotations

from pixel.orchestrator.fallbacks import ORG_ABSTAIN
from pixel.voice.speech_text import speech_text_for_tts


def test_strips_urls_and_keeps_grounded_meaning() -> None:
    spoken = speech_text_for_tts(ORG_ABSTAIN)
    assert "https://" not in spoken
    assert "http://" not in spoken
    assert "cannot verify" in spoken.lower()
    assert "Cyber Florida" in spoken or "official" in spoken.lower()


def test_does_not_invent_a_second_answer() -> None:
    text = "Phishing is a social-engineering trick. Do not click the link."
    assert speech_text_for_tts(text).startswith("Phishing is a social-engineering trick")


def test_adds_screen_note_for_sources_without_reading_urls() -> None:
    spoken = speech_text_for_tts(
        "Cyber Florida is the Florida Center for Cybersecurity. See https://cyberflorida.org/about/",
        has_sources=True,
    )
    assert "https://" not in spoken
    assert "on screen" in spoken.lower()


def test_tool_actions_point_to_the_screen() -> None:
    spoken = speech_text_for_tts(
        "Here is the FirstLine program page.",
        has_actions=True,
    )
    assert "https://" not in spoken
    assert "resource" in spoken.lower() or "on screen" in spoken.lower()


def test_limits_spoken_length() -> None:
    sentences = " ".join(f"Step {index} is important." for index in range(1, 8))
    spoken = speech_text_for_tts(sentences, has_sources=True)
    assert spoken.count(".") <= 5
    assert "Step 7" not in spoken
