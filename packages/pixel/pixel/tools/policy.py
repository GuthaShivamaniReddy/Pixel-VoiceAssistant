"""Server-side permission and confirmation. Never trust the model or retrieved text."""

from __future__ import annotations

import re

from pixel.tools.types import AuthContext, ConfirmationState, Permission, ToolDefinition

_CONFIRM = re.compile(
    r"^(yes|yep|yeah|ok|okay|confirm|please (do|open)|go ahead|do it)([\s.!?]*)$",
    re.I,
)

_RANK: dict[Permission, int] = {"public": 0, "authenticated": 1, "privileged": 2}


def permission_allows(auth: AuthContext, required: Permission) -> bool:
    return _RANK[auth.permission] >= _RANK[required]


def is_explicit_confirmation(text: str) -> bool:
    return bool(_CONFIRM.match(" ".join(text.lower().split()).strip()))


def confirmation_satisfied(definition: ToolDefinition, state: ConfirmationState) -> bool:
    if definition.confirmation_policy == "none":
        return True
    if definition.confirmation_policy == "ui_click":
        return True
    if definition.confirmation_policy != "explicit":
        return False
    if not state.required:
        return False
    if not state.confirmed:
        return False
    return state.confirmed_tool == definition.name
