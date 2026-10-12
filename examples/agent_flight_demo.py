"""End-to-end demonstration of recording, replaying, and inspecting an AI agent run."""

from __future__ import annotations

import httpx
from pathlib import Path
from rerunner import CassetteTransport, side_effect


@side_effect(name="save_report_to_db")
def save_report(title: str, content: str) -> str:
    print(f"[DB ACTION] Writing '{title}' to internal database...")
    return "row_id_48291"


def run_agent(transport: httpx.BaseTransport) -> str:
    with httpx.Client(transport=transport) as client:
        # Step 1: Reason about user query
        print("\n--> Step 1: Calling LLM to analyze query...")
        resp1 = client.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": "Generate executive financial briefing."}],
            },
        )
        print(f"    Received: {resp1.status_code}")

        # Step 2: Guarded tool execution
        print("--> Step 2: Saving briefing...")
        row_id = save_report("Q3 Briefing", resp1.text)
        print(f"    Report stored with ID: {row_id}")

        # Step 3: Confirmation call
        print("--> Step 3: Calling LLM to generate summary notification...")
        resp2 = client.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": f"Confirm storage of report {row_id}"}],
            },
        )
        print(f"    Received: {resp2.status_code}")
        return resp2.text


if __name__ == "__main__":
    cassette_file = Path("demo_session.jsonl")

    # MOCK TRANSPORT FOR LOCAL DEMO (In production, uses real OpenAI or Anthropic API)
    class DemoNetwork(httpx.BaseTransport):
        def handle_request(self, request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                headers={"content-type": "application/json"},
                content=b'{"choices": [{"message": {"content": "Financial briefing approved and verified."}}]}',
                request=request,
            )

    print("========================================")
    print("PHASE 1: RECORDING AGENT RUN")
    print("========================================")
    record_transport = CassetteTransport(cassette_file, mode="record", real_transport=DemoNetwork())
    run_agent(record_transport)

    print("\n========================================")
    print("PHASE 2: DETERMINISTIC $0 REPLAY IN CI")
    print("========================================")
    # Notice: Zero network requests are made, DB action is skipped safely
    replay_transport = CassetteTransport(cassette_file, mode="replay")
    run_agent(replay_transport)

    print("\n[SUCCESS] Agent executed deterministically from cassette!")
