"""Unit tests for automated secret, API key, and PII redactor."""

from __future__ import annotations

from rerunner.sanitizer import sanitize_headers, sanitize_payload, sanitize_string


def test_sanitize_anthropic_and_openai_keys() -> None:
    text = "Using key sk-ant-api03-abcdef1234567890abcdef1234567890 and sk-proj-1234567890abcdef1234567890123456"
    cleaned = sanitize_string(text)
    assert "sk-ant" not in cleaned
    assert "[REDACTED_ANTHROPIC_KEY]" in cleaned
    assert "sk-proj" not in cleaned
    assert "[REDACTED_OPENAI_PROJECT_KEY]" in cleaned


def test_sanitize_headers() -> None:
    headers = {
        "Authorization": "Bearer secret_jwt_token_12345",
        "X-Api-Key": "my-secret-key",
        "Content-Type": "application/json",
    }
    cleaned = sanitize_headers(headers)
    assert cleaned["authorization"] == "[REDACTED]"
    assert cleaned["x-api-key"] == "[REDACTED]"
    assert cleaned["content-type"] == "application/json"


def test_sanitize_nested_payload() -> None:
    payload = {
        "prompt": "Here is key sk-12345678901234567890123456789012",
        "nested": ["Bearer secret_token_xyz_12345"],
    }
    cleaned = sanitize_payload(payload)
    assert "[REDACTED_OPENAI_KEY]" in cleaned["prompt"]
    assert "Bearer [REDACTED_TOKEN]" in cleaned["nested"][0]
