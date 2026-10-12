"""Tolerant request matcher and normalizer for AI agent HTTP interactions."""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

if TYPE_CHECKING:
    from rerunner.models import RecordedRequest

# Headers that frequently vary across environments or runs without changing semantic meaning
VOLATILE_HEADER_PREFIXES = (
    "x-stainless-",  # Anthropic & OpenAI SDK metadata
    "x-amzn-",
    "x-goog-",
)

VOLATILE_HEADER_NAMES = {
    "date",
    "x-request-id",
    "request-id",
    "traceparent",
    "tracestate",
    "user-agent",
    "content-length",
    "content-encoding",
    "authorization",
    "host",
    "connection",
    "keep-alive",
}


def normalize_headers(headers: dict[str, str]) -> dict[str, str]:
    """Strip non-deterministic and credential headers, normalizing keys to lowercase."""
    normalized: dict[str, str] = {}
    for key, value in headers.items():
        k_lower = key.lower().strip()
        if k_lower in VOLATILE_HEADER_NAMES:
            continue
        if any(k_lower.startswith(prefix) for prefix in VOLATILE_HEADER_PREFIXES):
            continue
        normalized[k_lower] = value.strip()
    return normalized


def normalize_body(body: bytes | str | None) -> str:
    """Normalize body by canonicalizing JSON if applicable, or trimming whitespace."""
    if body is None:
        return ""
    if isinstance(body, bytes):
        try:
            body_str = body.decode("utf-8")
        except UnicodeDecodeError:
            return body.hex()
    else:
        body_str = body

    body_str = body_str.strip()
    if not body_str:
        return ""

    try:
        parsed = json.loads(body_str)
        # Canonical JSON: sorted keys, compact separators
        return json.dumps(parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except Exception:
        return body_str


def normalize_url(url: str) -> str:
    """Normalize URL by sorting query parameters."""
    parsed = urlparse(url)
    if not parsed.query:
        return url
    query_params = sorted(parse_qsl(parsed.query))
    normalized_query = urlencode(query_params)
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            normalized_query,
            parsed.fragment,
        )
    )


def compute_request_key(method: str, url: str, body: bytes | str | None = None) -> str:
    """Compute deterministic SHA-256 hash identifying an HTTP request."""
    norm_url = normalize_url(url)
    norm_body = normalize_body(body)
    payload = f"{method.upper()}|{norm_url}|{norm_body}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def request_matches(
    recorded: RecordedRequest,
    incoming_method: str,
    incoming_url: str,
    incoming_body: bytes | str | None = None,
) -> bool:
    """Determine whether an incoming request matches a recorded request."""
    incoming_key = compute_request_key(incoming_method, incoming_url, incoming_body)
    return recorded.request_key == incoming_key
