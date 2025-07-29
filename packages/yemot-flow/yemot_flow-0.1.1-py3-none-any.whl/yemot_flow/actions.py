
# -----------------------------
# File: yemot_router/actions.py
# -----------------------------
"""Low‑level builders that convert high‑level commands to Yemot response strings."""
from __future__ import annotations

from typing import List, Tuple

from .utils import urlencode, sanitize_text

Message = Tuple[str, str]  # (type, data)

_PREFIX = {
    "text": "t",
    "file": "f",
    "speech": "s",
    "digits": "d",
    "number": "n",
    "alpha": "a",
}


def build_id_list_message(messages: List[Message], *, remove_invalid_chars: bool | None = None) -> str:
    parts = []
    for m_type, data in messages:
        clean_data = sanitize_text(data) if remove_invalid_chars else data
        prefix = _PREFIX.get(m_type, m_type)
        parts.append(f"{prefix}-{urlencode(clean_data)}")
    joined = ".".join(parts)
    return f"id_list_message={joined}"


def build_read(messages: List[Message], *, mode: str = "tap", **options) -> str:
    # Yamot expects: first the messages (id_list_message), then read=...
    msg_line = build_id_list_message(messages)
    opts = "&".join(f"{k}={v}" for k, v in options.items())
    read_line = f"read={mode}{('&' + opts) if opts else ''}"
    return f"{msg_line}\n{read_line}"


def build_go_to_folder(folder: str) -> str:
    if folder != "hangup" and not folder.startswith("/"):
        folder = "/" + folder
    return f"go_to_folder={folder}"
