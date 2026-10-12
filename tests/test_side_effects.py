"""Unit tests for side-effects safe stubbing."""

from __future__ import annotations

from pathlib import Path
from rerunner.session import record, replay
from rerunner.side_effects import side_effect


def test_side_effect_recorded_and_stubbed(temp_cassette_path: Path) -> None:
    external_calls = 0

    @side_effect(name="send_payment")
    def charge_customer(amount: int) -> str:
        nonlocal external_calls
        external_calls += 1
        return f"txn_{amount}_success"

    # 1. Record run: function executes live
    with record(temp_cassette_path):
        res1 = charge_customer(100)
        assert res1 == "txn_100_success"
        assert external_calls == 1

    # 2. Replay run: function is NOT executed, returns recorded value
    with replay(temp_cassette_path):
        res2 = charge_customer(100)
        assert res2 == "txn_100_success"
        # external_calls is STILL 1! Real payment was safely skipped.
        assert external_calls == 1
