"""Rerunner: Deterministic flight recorder, replay engine, and CI test runner for AI agents."""

from __future__ import annotations

from rerunner.async_transport import AsyncCassetteTransport
from rerunner.cassette import Cassette, CassetteError
from rerunner.session import fork, record, replay
from rerunner.side_effects import side_effect
from rerunner.transport import CassetteTransport

__version__ = "0.1.0"

__all__ = [
    "AsyncCassetteTransport",
    "Cassette",
    "CassetteError",
    "CassetteTransport",
    "fork",
    "record",
    "replay",
    "side_effect",
]
