"""Zero-friction wrapper for the official Anthropic Claude SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal
import httpx
from rerunner.transport import CassetteTransport

if TYPE_CHECKING:
    from pathlib import Path


def wrap_anthropic(
    client: Any,
    cassette_path: Path | str,
    mode: Literal["record", "replay", "fork"] = "replay",
    fork_step: int | None = None,
) -> Any:
    """Attach a Rerunner CassetteTransport to an existing Anthropic client instance.

    Example:
        import anthropic
        from rerunner.integrations import wrap_anthropic

        client = wrap_anthropic(anthropic.Anthropic(), "my_run.jsonl", mode="replay")
    """
    transport = CassetteTransport(cassette_path=cassette_path, mode=mode, fork_step=fork_step)
    # The official Anthropic SDK uses an internal httpx._client.Client or _client
    if hasattr(client, "_client") and hasattr(client._client, "_transport"):
        client._client._transport = transport
    else:
        # Fallback to replacing http_client
        setattr(client, "_client", httpx.Client(transport=transport))

    return client
