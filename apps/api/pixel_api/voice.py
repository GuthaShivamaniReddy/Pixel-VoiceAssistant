from __future__ import annotations

import asyncio
import base64
import json
import logging
from typing import Any

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from pixel.domain import InputMode, Intent
from pixel.knowledge.registry import get_approved_source
from pixel.orchestrator import TurnError, run_text_turn, run_voice_turn
from pixel.orchestrator.process import OrchestratorConfig
from pixel.orchestrator.session import ConversationSession, SessionError
from pixel.providers import ProviderConfigError
from pixel.security.audit import record_security_event
from pixel.security.limits import InProcessRateLimiter, client_ip
from pixel.shared.cancellation import CancelledError
from pixel.tools.types import AuthContext, SourceOffer
from pixel.voice import AudioBuffer
from pixel_api.runtime import VoiceRuntime

log = logging.getLogger("pixel.api")


class TurnRequest(BaseModel):
    session_id: str | None = Field(default=None, max_length=64)
    turn_id: str = Field(min_length=1, max_length=128)
    text: str = Field(max_length=8000)
    speak: bool = True


def _public_error(code: str, message: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message}}


def _session_payload(session: ConversationSession) -> dict[str, Any]:
    return {
        "session_id": session.id,
        "created_at": session.created_at.isoformat(),
        "expires_at": session.expires_at.isoformat(),
        "policy_version": session.policy_version,
        "capabilities": {"text": session.capabilities.text, "voice": session.capabilities.voice},
    }


def _timings_payload(result) -> dict[str, int | None]:
    return {
        "time_to_transcript_ms": result.timings.time_to_transcript_ms,
        "model_latency_ms": result.timings.model_latency_ms,
        "tts_latency_ms": result.timings.tts_latency_ms,
        "time_to_first_audio_ms": result.timings.time_to_first_audio_ms,
        "total_turn_latency_ms": result.timings.total_turn_latency_ms,
        "retrieval_latency_ms": result.timings.retrieval_latency_ms,
    }


def _success_body(session: ConversationSession, result, *, include_audio: bool) -> dict[str, Any]:
    audio_b64 = None
    if include_audio and result.wav_bytes:
        audio_b64 = base64.b64encode(result.wav_bytes).decode("ascii")
    return {
        "session_id": session.id,
        "transcript": result.transcript,
        "text": result.reply_text,
        "sources": result.sources,
        "citations": result.citations,
        "actions": result.actions,
        "status": result.status,
        "policy_version": result.policy_version,
        "audio_wav_base64": audio_b64,
        "metrics": _timings_payload(result),
        "voice_warning": result.error_code,
    }


def _orchestrator_config(runtime: VoiceRuntime) -> OrchestratorConfig:
    return OrchestratorConfig(
        max_user_chars=runtime.settings.max_user_chars,
        max_attempts=runtime.settings.llm_max_attempts,
        backoff_seconds=runtime.settings.llm_retry_backoff_seconds,
        voice_id=runtime.settings.openai_tts_voice,
        tool_timeout_seconds=runtime.settings.tool_timeout_seconds,
        max_tool_calls_per_turn=runtime.settings.max_tool_calls_per_turn,
        kill_switch=runtime.settings.kill_switch(),
    )


def _rate_limited(retry_after: int) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        headers={"Retry-After": str(retry_after)},
        content={
            "error": {
                "code": "rate_limited",
                "message": "Too many requests. Please wait and try again.",
            }
        },
    )


def _client_ip(request: Request, runtime: VoiceRuntime) -> str:
    host = request.client.host if request.client else None
    return client_ip(
        host,
        forwarded=request.headers.get("x-forwarded-for"),
        trust_proxy=runtime.settings.trust_proxy,
    )


def _enforce_rate(
    request: Request,
    runtime: VoiceRuntime,
    key: str,
    limit: int,
    *,
    correlation_id: str = "",
) -> JSONResponse | None:
    if not runtime.settings.rate_limit_enabled:
        return None
    limiter: InProcessRateLimiter | None = getattr(request.app.state, "rate_limiter", None)
    if limiter is None:
        return None
    allowed, retry_after = limiter.check(key, limit=limit)
    if allowed:
        return None
    record_security_event(
        kind="rate_limited", detail=key.split(":", 1)[0], correlation_id=correlation_id
    )
    return _rate_limited(retry_after)


def _offers_from_result(result) -> tuple[SourceOffer, ...]:
    offers: list[SourceOffer] = []
    seen: set[str] = set()
    rows = list(result.sources) + list(result.actions)
    for item in rows:
        if not isinstance(item, dict):
            continue
        url = item.get("url") or item.get("href") or ""
        approved = get_approved_source(str(url))
        if approved is None or approved.id in seen:
            continue
        seen.add(approved.id)
        offers.append(
            SourceOffer(source_id=approved.id, title=approved.title, url=approved.canonical_url)
        )
    return tuple(offers)


def _auth(session: ConversationSession, turn_id: str, correlation_id: str) -> AuthContext:
    return AuthContext(
        permission="public",
        session_id=session.id,
        turn_id=turn_id,
        correlation_id=correlation_id,
    )


def _commit(session: ConversationSession, generation: int, turn_id: str, result) -> bool:
    intent = Intent(result.intent) if result.intent else None
    return session.commit_turn(
        generation=generation,
        turn_id=turn_id,
        user_text=result.transcript,
        assistant_text=result.reply_text,
        intent=intent,
        offers=_offers_from_result(result),
    )


def build_voice_router(runtime: VoiceRuntime) -> APIRouter:
    router = APIRouter()

    @router.post("/v1/sessions")
    def create_session(request: Request) -> JSONResponse:
        blocked = _enforce_rate(
            request,
            runtime,
            f"session:{_client_ip(request, runtime)}",
            runtime.settings.rate_limit_session_per_minute,
        )
        if blocked is not None:
            return blocked
        session = runtime.store.create()
        log.info("session_create session=%s", session.id)
        return JSONResponse(status_code=201, content=_session_payload(session))

    @router.post("/v1/sessions/{session_id}/clear")
    def clear_session(session_id: str) -> JSONResponse:
        if len(session_id) > 64:
            return JSONResponse(
                status_code=400,
                content=_public_error(
                    "invalid_input", "That conversation was not found. Start again."
                ),
            )
        try:
            session = runtime.store.clear(session_id)
        except SessionError as exc:
            status = 410 if exc.code == "session_expired" else 404
            return JSONResponse(status_code=status, content=_public_error(exc.code, exc.message))
        log.info("session_clear session=%s", session.id)
        return JSONResponse(status_code=200, content={"session_id": session.id, "cleared": True})

    @router.post("/v1/turns")
    async def create_turn(payload: TurnRequest, request: Request) -> JSONResponse:
        correlation_id = getattr(request.state, "correlation_id", "")
        ip = _client_ip(request, runtime)
        blocked = _enforce_rate(
            request,
            runtime,
            f"turn:{ip}",
            runtime.settings.rate_limit_turn_per_minute,
            correlation_id=str(correlation_id),
        )
        if blocked is not None:
            return blocked
        if payload.session_id:
            blocked = _enforce_rate(
                request,
                runtime,
                f"turn-session:{payload.session_id}",
                runtime.settings.rate_limit_turn_per_session_per_minute,
                correlation_id=str(correlation_id),
            )
            if blocked is not None:
                return blocked
        try:
            session = runtime.session(payload.session_id)
        except SessionError as exc:
            status = 410 if exc.code == "session_expired" else 404
            return JSONResponse(status_code=status, content=_public_error(exc.code, exc.message))
        active = runtime.store.begin_turn(session, payload.turn_id, input_mode=InputMode.text)
        cancellation = active.cancellation
        generation = active.generation
        try:
            result = await asyncio.to_thread(
                run_text_turn,
                text=payload.text,
                llm=runtime.providers.llm,
                tts=runtime.providers.tts,
                cancellation=cancellation,
                history=session.history_tuple(),
                last_intent=session.last_intent,
                speak=payload.speak,
                voice_id=runtime.settings.openai_tts_voice,
                config=_orchestrator_config(runtime),
                retriever=runtime.retriever,
                last_offers=tuple(session.last_offers),
                auth=_auth(session, payload.turn_id, correlation_id),
            )
        except CancelledError:
            return JSONResponse(
                status_code=409, content=_public_error("cancelled", "Turn cancelled.")
            )
        except ProviderConfigError:
            return JSONResponse(
                status_code=503,
                content=_public_error("response_failure", "Voice providers are not configured."),
            )
        except TurnError as exc:
            log.info(
                "turn_error correlation=%s session=%s turn=%s code=%s",
                correlation_id,
                session.id,
                payload.turn_id,
                exc.code,
            )
            status = 400 if exc.code in {"empty", "invalid_input"} else 502
            return JSONResponse(status_code=status, content=_public_error(exc.code, exc.message))
        finally:
            runtime.store.take_turn(session, payload.turn_id)

        if cancellation.is_cancelled():
            return JSONResponse(
                status_code=409, content=_public_error("cancelled", "Turn cancelled.")
            )
        if not _commit(session, generation, payload.turn_id, result):
            return JSONResponse(
                status_code=409, content=_public_error("cancelled", "Turn cancelled.")
            )
        log.info(
            "turn_complete correlation=%s session=%s turn=%s intent=%s status=%s",
            correlation_id,
            session.id,
            payload.turn_id,
            result.intent,
            result.status,
        )
        body = _success_body(session, result, include_audio=payload.speak)
        body["turn_id"] = payload.turn_id
        body["correlation_id"] = correlation_id
        return JSONResponse(status_code=200, content=body)

    @router.websocket("/v1/realtime")
    async def realtime(websocket: WebSocket) -> None:
        origin = websocket.headers.get("origin")
        allowed = set(runtime.settings.cors_origin_list())
        if runtime.settings.pixel_env == "production" and not origin:
            await websocket.close(code=1008)
            return
        if origin and origin not in allowed:
            await websocket.close(code=1008)
            return
        limiter: InProcessRateLimiter | None = getattr(websocket.app.state, "rate_limiter", None)
        if runtime.settings.rate_limit_enabled and limiter is not None:
            host = websocket.client.host if websocket.client else None
            ip = client_ip(
                host,
                forwarded=websocket.headers.get("x-forwarded-for"),
                trust_proxy=runtime.settings.trust_proxy,
            )
            allowed_ws, _retry = limiter.check(
                f"ws:{ip}", limit=runtime.settings.rate_limit_ws_per_minute
            )
            if not allowed_ws:
                await websocket.close(code=1013)
                return
        await websocket.accept()
        session = runtime.store.create()
        try:
            await websocket.send_json({"type": "hello_ok", "session_id": session.id})
            while True:
                message = await websocket.receive()
                if message.get("type") == "websocket.disconnect":
                    break
                if message.get("bytes") is not None:
                    active = session.active
                    if active is not None:
                        runtime.append_audio(session, active.turn_id, message["bytes"])
                    continue
                text = message.get("text")
                if not text:
                    continue
                if len(text) > runtime.settings.max_ws_control_bytes:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "code": "payload_too_large",
                            "message": "That request is too large.",
                        }
                    )
                    continue
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "code": "generic",
                            "message": "Malformed control message.",
                        }
                    )
                    continue
                session = await _handle_control(runtime, session, websocket, payload)
        except WebSocketDisconnect:
            if session.active:
                session.active.cancellation.cancel()
        except Exception:
            log.info("realtime_socket_closed session=%s", session.id)
            if session.active:
                session.active.cancellation.cancel()

    return router


async def _handle_control(
    runtime: VoiceRuntime,
    session: ConversationSession,
    websocket: WebSocket,
    payload: dict[str, Any],
) -> ConversationSession:
    kind = str(payload.get("type") or "")
    turn_id = str(payload.get("turn_id") or "")
    if kind == "hello":
        requested = payload.get("session_id")
        if requested:
            try:
                session = runtime.store.get(str(requested))
            except SessionError as exc:
                await websocket.send_json(
                    {"type": "error", "code": exc.code, "message": exc.message}
                )
                return session
        await websocket.send_json({"type": "hello_ok", "session_id": session.id})
        return session
    if kind == "start_turn":
        sample_rate = int(payload.get("sample_rate") or 16000)
        runtime.store.begin_turn(
            session, turn_id, input_mode=InputMode.voice, sample_rate=sample_rate
        )
        await websocket.send_json({"type": "turn_accepted", "turn_id": turn_id})
        return session
    if kind == "cancel":
        runtime.store.cancel_turn(session, turn_id)
        await websocket.send_json({"type": "cancelled", "turn_id": turn_id})
        return session
    if kind == "end_turn":
        await _finish_voice_turn(runtime, session, websocket, turn_id)
    return session


async def _finish_voice_turn(
    runtime: VoiceRuntime,
    session: ConversationSession,
    websocket: WebSocket,
    turn_id: str,
) -> None:
    active = runtime.store.take_turn(session, turn_id)
    if active is None:
        await websocket.send_json(
            {"type": "error", "turn_id": turn_id, "code": "generic", "message": "No active turn."}
        )
        return
    audio = AudioBuffer(pcm16le=bytes(active.pcm), sample_rate=active.sample_rate)
    try:
        result = await asyncio.to_thread(
            run_voice_turn,
            audio=audio,
            stt=runtime.providers.stt,
            llm=runtime.providers.llm,
            tts=runtime.providers.tts,
            cancellation=active.cancellation,
            history=session.history_tuple(),
            last_intent=session.last_intent,
            speak=True,
            voice_id=runtime.settings.openai_tts_voice,
            config=_orchestrator_config(runtime),
            retriever=runtime.retriever,
            last_offers=tuple(session.last_offers),
            auth=_auth(session, turn_id, ""),
        )
    except CancelledError:
        await websocket.send_json({"type": "cancelled", "turn_id": turn_id})
        return
    except ProviderConfigError:
        await websocket.send_json(
            {
                "type": "error",
                "turn_id": turn_id,
                "code": "response_failure",
                "message": "Voice providers are not configured.",
            }
        )
        return
    except TurnError as exc:
        await websocket.send_json(
            {"type": "error", "turn_id": turn_id, "code": exc.code, "message": exc.message}
        )
        return
    if active.cancellation.is_cancelled():
        await websocket.send_json({"type": "cancelled", "turn_id": turn_id})
        return
    if not _commit(session, active.generation, turn_id, result):
        await websocket.send_json({"type": "cancelled", "turn_id": turn_id})
        return
    await websocket.send_json(
        {"type": "final_transcript", "turn_id": turn_id, "text": result.transcript}
    )
    await websocket.send_json(
        {
            "type": "assistant_text",
            "turn_id": turn_id,
            "text": result.reply_text,
            "sources": result.sources,
            "actions": result.actions,
            "citations": result.citations,
            "voice_warning": result.error_code,
        }
    )
    if result.wav_bytes:
        await websocket.send_json({"type": "audio_start", "turn_id": turn_id, "mime": "audio/wav"})
        await websocket.send_bytes(result.wav_bytes)
        await websocket.send_json({"type": "audio_end", "turn_id": turn_id})
    await websocket.send_json({"type": "metrics", "turn_id": turn_id, **_timings_payload(result)})
    await websocket.send_json({"type": "turn_complete", "turn_id": turn_id})
