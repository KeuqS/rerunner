"""Zero-friction wrapper for the official OpenAI SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal
import httpx
from rerunner.transport import CassetteTransport

if TYPE_CHECKING:
    from pathlib import Path


def wrap_openai(
    client: Any,
    cassette_path: Path | str,
    mode: Literal["record", "replay", "fork"] = "replay",
    fork_step: int | None = None,
) -> Any:
    """Attach a Rerunner CassetteTransport to an existing OpenAI client instance.

    Example:
        import openai
        from rerunner.integrations import wrap_openai

        client = wrap_openai(openai.OpenAI(), "my_run.jsonl", mode="replay")
    """
    transport = CassetteTransport(cassette_path=cassette_path, mode=mode, fork_step=fork_step)
    if hasattr(client, "_client") and hasattr(client._client, "_transport"):
        client._client._transport = transport
    else:
        client._client = httpx.Client(transport=transport)

    return client
