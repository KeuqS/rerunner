"""Asynchronous httpx.AsyncBaseTransport implementation for recording and replaying HTTP requests."""

from __future__ import annotations

import httpx
from typing import Literal
from pathlib import Path
from rerunner.cassette import Cassette, CassetteError
from rerunner.matcher import (
    compute_request_key,
    normalize_body,
    normalize_headers,
)
from rerunner.models import CassetteEntry, RecordedRequest, RecordedResponse
from rerunner.sanitizer import sanitize_headers, sanitize_string


class AsyncCassetteTransport(httpx.AsyncBaseTransport):
    """Custom asynchronous httpx transport that records or replays network traffic via a cassette."""

    def __init__(
        self,
        cassette_path: Path | str,
        mode: Literal["record", "replay", "fork"] = "replay",
        fork_step: int | None = None,
        real_transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.cassette_path = Path(cassette_path)
        self.mode = mode
        self.fork_step = fork_step
        self.real_transport = real_transport or httpx.AsyncHTTPTransport()
        self.current_step = 0

        if self.mode in ("replay", "fork") and self.cassette_path.exists():
            self.cassette = Cassette.load(self.cassette_path)
        else:
            self.cassette = Cassette(self.cassette_path)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.current_step += 1
        body_bytes = await request.aread()
        request_key = compute_request_key(request.method, str(request.url), body_bytes)

        # Check whether to replay
        should_replay = (
            self.mode == "replay"
            or (self.mode == "fork" and self.fork_step is not None and self.current_step <= self.fork_step)
        )

        if should_replay:
            match = self.cassette.find_http_match(request_key)
            if match is None or match.response is None:
                raise CassetteError(
                    f"[Async Step {self.current_step}] No cassette match found in replay mode for "
                    f"{request.method} {request.url} (key: {request_key[:12]}...)"
                )

            return httpx.Response(
                status_code=match.response.status_code,
                headers=match.response.headers,
                content=match.response.body.encode("utf-8"),
                request=request,
            )

        # LIVE EXECUTION
        real_response = await self.real_transport.handle_async_request(request)
        response_bytes = await real_response.aread()

        # Sanitize headers and body before writing to disk
        cleaned_headers = sanitize_headers(normalize_headers(dict(request.headers)))
        cleaned_req_body = sanitize_string(normalize_body(body_bytes))
        cleaned_resp_body = sanitize_string(response_bytes.decode("utf-8", errors="replace"))

        # Record to cassette
        recorded_req = RecordedRequest(
            method=request.method,
            url=str(request.url),
            headers=cleaned_headers,
            body=cleaned_req_body,
            request_key=request_key,
        )

        recorded_resp = RecordedResponse(
            status_code=real_response.status_code,
            headers=sanitize_headers(dict(real_response.headers)),
            body=cleaned_resp_body,
            http_version=real_response.extensions.get("http_version", b"HTTP/1.1").decode("ascii", errors="ignore"),
        )

        entry = CassetteEntry(
            step=self.current_step,
            entry_type="http",
            request=recorded_req,
            response=recorded_resp,
        )
        self.cassette.append(entry)
        self.cassette.save()

        return httpx.Response(
            status_code=real_response.status_code,
            headers=real_response.headers,
            content=response_bytes,
            request=request,
        )

    async def aclose(self) -> None:
        if hasattr(self.real_transport, "aclose"):
            await self.real_transport.aclose()
