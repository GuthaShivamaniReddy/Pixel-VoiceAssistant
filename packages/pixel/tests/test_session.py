from datetime import timedelta

from pixel.domain import InputMode, Intent
from pixel.orchestrator.session import MAX_MESSAGES, SessionError, SessionStore


def test_create_and_get_session() -> None:
    store = SessionStore(ttl_seconds=60)
    created = store.create()
    loaded = store.get(created.id)
    assert loaded.id == created.id
    assert loaded.policy_version


def test_unknown_session() -> None:
    store = SessionStore(ttl_seconds=60)
    try:
        store.get("missing")
    except SessionError as exc:
        assert exc.code == "unknown_session"
    else:
        raise AssertionError("expected unknown_session")


def test_history_is_bounded() -> None:
    store = SessionStore(ttl_seconds=60)
    session = store.create()
    for index in range(10):
        session.generation = index + 1
        session.commit_turn(
            generation=session.generation,
            turn_id=f"t{index}",
            user_text=f"user {index}",
            assistant_text=f"pixel {index}",
            intent=Intent.unsupported,
        )
    assert len(session.messages) == MAX_MESSAGES


def test_clear_then_follow_up_has_no_referent() -> None:
    store = SessionStore(ttl_seconds=60)
    session = store.create()
    session.commit_turn(
        generation=0,
        turn_id="t1",
        user_text="What programs are available?",
        assistant_text="See the public site.",
        intent=Intent.cyberflorida_knowledge,
    )
    store.clear(session.id)
    assert store.get(session.id).history_tuple() == ()


def test_concurrent_begin_cancels_previous() -> None:
    store = SessionStore(ttl_seconds=60)
    session = store.create()
    first = store.begin_turn(session, "a", input_mode=InputMode.text)
    store.begin_turn(session, "b", input_mode=InputMode.voice)
    assert first.cancellation.is_cancelled()
    assert session.active is not None
    assert session.active.turn_id == "b"


def test_expiry_uses_ttl() -> None:
    store = SessionStore(ttl_seconds=30)
    session = store.create()
    session.expires_at = session.created_at - timedelta(seconds=1)
    try:
        store.get(session.id)
    except SessionError as exc:
        assert exc.code == "session_expired"
    else:
        raise AssertionError("expected expiry")
