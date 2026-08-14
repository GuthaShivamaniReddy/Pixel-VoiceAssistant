from __future__ import annotations

import logging

from pixel.knowledge.retrieve import KnowledgeRetriever
from pixel.knowledge.runtime import fixture_retriever
from pixel.orchestrator.session import ConversationSession, SessionStore
from pixel.providers import ProviderBundle, build_providers
from pixel_api.settings import Settings

log = logging.getLogger("pixel.api")

MAX_AUDIO_BYTES = 1_000_000


class VoiceRuntime:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = SessionStore(ttl_seconds=settings.session_ttl_seconds)
        self._providers: ProviderBundle | None = None
        self._retriever: KnowledgeRetriever | None = None

    @property
    def providers(self) -> ProviderBundle:
        if self._providers is None:
            self._providers = build_providers(
                llm_provider=self.settings.llm_provider,
                stt_provider=self.settings.stt_provider,
                tts_provider=self.settings.tts_provider,
                openai_api_key=self.settings.openai_api_key,
                allow_mock=self.settings.allow_mock_providers(),
                stt_timeout_seconds=self.settings.stt_timeout_seconds,
                llm_timeout_seconds=self.settings.llm_timeout_seconds,
                tts_timeout_seconds=self.settings.tts_timeout_seconds,
                openai_stt_model=self.settings.openai_stt_model,
                openai_llm_model=self.settings.openai_llm_model,
                openai_tts_model=self.settings.openai_tts_model,
            )
        return self._providers

    @property
    def retriever(self) -> KnowledgeRetriever:
        if self._retriever is None:
            item = fixture_retriever()
            item.top_k = self.settings.retrieval_top_k
            item.min_score = self.settings.retrieval_min_score
            self._retriever = item
        return self._retriever

    def session(self, session_id: str | None) -> ConversationSession:
        return self.store.get_or_create(session_id)

    def append_audio(self, session: ConversationSession, turn_id: str, chunk: bytes) -> None:
        active = session.active
        if active is None or active.turn_id != turn_id:
            return
        remaining = MAX_AUDIO_BYTES - len(active.pcm)
        if remaining <= 0:
            return
        active.pcm.extend(chunk[:remaining])
