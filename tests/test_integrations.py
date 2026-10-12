"""Unit tests for official framework adapters and wrappers."""

from __future__ import annotations

import httpx
from pathlib import Path
from rerunner.integrations.anthropic import wrap_anthropic
from rerunner.integrations.langchain import RerunnerCallbackHandler
from rerunner.integrations.openai import wrap_openai


class DummyClient:
    def __init__(self) -> None:
        self._client = httpx.Client()


def test_wrap_anthropic(temp_cassette_path: Path) -> None:
    client = DummyClient()
    wrapped = wrap_anthropic(client, temp_cassette_path, mode="record")
    assert hasattr(wrapped._client, "_transport")


def test_wrap_openai(temp_cassette_path: Path) -> None:
    client = DummyClient()
    wrapped = wrap_openai(client, temp_cassette_path, mode="record")
    assert hasattr(wrapped._client, "_transport")


def test_langchain_callback_handler(temp_cassette_path: Path) -> None:
    handler = RerunnerCallbackHandler(str(temp_cassette_path), mode="record")
    handler.on_llm_start({}, ["Write code"])
    handler.on_tool_start({}, "Search web")
    assert handler.step_count == 2
