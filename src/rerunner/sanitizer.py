"""Automated secret, API key, and PII redactor for safe cassette persistence."""

from __future__ import annotations

import re
from typing import Any

# Regular expressions detecting common API keys and sensitive tokens
SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"sk-ant-[a-zA-Z0-9_\-]{32,}", re.IGNORECASE), "[REDACTED_ANTHROPIC_KEY]"),
    (re.compile(r"sk-proj-[a-zA-Z0-9_\-]{32,}", re.IGNORECASE), "[REDACTED_OPENAI_PROJECT_KEY]"),
    (re.compile(r"sk-[a-zA-Z0-9]{32,}", re.IGNORECASE), "[REDACTED_OPENAI_KEY]"),
    (re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]{16,}", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
    (re.compile(r"ghp_[a-zA-Z0-9]{36,}", re.IGNORECASE), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE), "[REDACTED_AWS_KEY_ID]"),
]

# Sensitive header keys that should always have their values scrubbed
SENSITIVE_HEADERS: set[str] = {
    "authorization",
    "x-api-key",
    "api-key",
    "proxy-authorization",
    "cookie",
    "set-cookie",
}


def sanitize_string(text: str) -> str:
    """Scan and scrub sensitive API tokens from arbitrary strings."""
    if not text:
        return text
    sanitized = text
    for pattern, replacement in SECRET_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    """Scrub sensitive HTTP headers before writing to cassette."""
    sanitized: dict[str, str] = {}
    for key, value in headers.items():
        k_lower = key.lower().strip()
        if k_lower in SENSITIVE_HEADERS:
            sanitized[k_lower] = "[REDACTED]"
        else:
            sanitized[k_lower] = sanitize_string(value)
    return sanitized


def sanitize_payload(data: Any) -> Any:
    """Recursively sanitize dicts, lists, and strings for safe storage."""
    if isinstance(data, str):
        return sanitize_string(data)
    if isinstance(data, dict):
        return {k: sanitize_payload(v) for k, v in data.items()}
    if isinstance(data, list):
        return [sanitize_payload(item) for item in data]
    return data
