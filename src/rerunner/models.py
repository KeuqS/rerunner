"""Pydantic v2 data models for Rerunner cassette recordings."""

from __future__ import annotations

import time
from typing import Any, Literal
from pydantic import BaseModel, Field


class RecordedRequest(BaseModel):
    """Normalized recorded HTTP request."""

    method: str
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    body: str = ""
    request_key: str = ""


class RecordedResponse(BaseModel):
    """Recorded HTTP response."""

    status_code: int
    headers: dict[str, str] = Field(default_factory=dict)
    body: str = ""
    is_base64: bool = False
    http_version: str = "HTTP/1.1"


class CassetteMetadata(BaseModel):
    """Metadata header written as the first line of every cassette."""

    format_version: str = "1.0.0"
    created_at: float = Field(default_factory=time.time)
    agent_id: str | None = None
    hash_algorithm: str = "sha256"


class CassetteEntry(BaseModel):
    """A single recorded event in the agent flight recorder (HTTP call or side-effect)."""

    step: int
    entry_type: Literal["http", "side_effect"] = "http"
    request: RecordedRequest | None = None
    response: RecordedResponse | None = None
    side_effect_name: str | None = None
    side_effect_args: list[Any] | None = None
    side_effect_kwargs: dict[str, Any] | None = None
    side_effect_result: Any | None = None
    prev_hash: str = "GENESIS"
    entry_hash: str = ""
    timestamp: float = Field(default_factory=time.time)
