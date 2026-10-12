"""Pytest plugin providing @pytest.mark.rerunner and the rerunner_transport fixture."""

from __future__ import annotations

from typing import TYPE_CHECKING
from collections.abc import Generator
import pytest
from rerunner.transport import CassetteTransport

if TYPE_CHECKING:
    import httpx


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register CLI flags for pytest."""
    group = parser.getgroup("rerunner")
    group.addoption(
        "--rerunner-record",
        action="store_true",
        default=False,
        help="Record new cassettes instead of replaying existing ones",
    )


@pytest.fixture
def rerunner_transport(
    request: pytest.FixtureRequest,
) -> Generator[httpx.BaseTransport, None, None]:
    """Pytest fixture providing a pre-configured CassetteTransport for the current test."""
    marker = request.node.get_closest_marker("rerunner")
    cassette_path = "cassette.jsonl"
    if marker and marker.args:
        cassette_path = str(marker.args[0])

    from typing import Literal

    is_record_mode = bool(request.config.getoption("--rerunner-record"))
    mode: Literal["record", "replay"] = "record" if is_record_mode else "replay"

    transport = CassetteTransport(cassette_path=cassette_path, mode=mode)
    yield transport
    transport.close()
