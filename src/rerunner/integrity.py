"""Cryptographic tamper-evident hash chaining for cassette verification."""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rerunner.models import CassetteEntry


def canonical_entry_payload(entry: CassetteEntry) -> str:
    """Create a deterministic JSON string representing the entry without its hash."""
    data = entry.model_dump(exclude={"entry_hash"})
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_entry_hash(entry: CassetteEntry, prev_hash: str) -> str:
    """Compute SHA-256 hash chaining prev_hash with canonical entry payload."""
    payload = f"{prev_hash}:{canonical_entry_payload(entry)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_cassette_integrity(entries: list[CassetteEntry]) -> tuple[bool, str | None]:
    """Verify that every entry in the cassette adheres to the cryptographic hash chain.

    Returns:
        (True, None) if the chain is fully verified and untampered.
        (False, error_message) if any link in the chain is broken or modified.
    """
    if not entries:
        return True, None

    expected_prev = "GENESIS"
    for entry in entries:
        if entry.prev_hash != expected_prev:
            return (
                False,
                f"Broken chain at step {entry.step}: expected prev_hash '{expected_prev}', got '{entry.prev_hash}'",
            )

        recomputed_hash = compute_entry_hash(entry, expected_prev)
        if recomputed_hash != entry.entry_hash:
            return (
                False,
                f"Tampered entry detected at step {entry.step}: recorded hash '{entry.entry_hash}' does not match recomputed '{recomputed_hash}'",
            )

        expected_prev = entry.entry_hash

    return True, None
