import asyncio
import logging

import pytest
from starlette.requests import Request

from api.main import log_requests


def _fake_request(path: str = "/boom") -> Request:
    scope = {"type": "http", "method": "GET", "path": path, "headers": []}
    return Request(scope)


def test_log_requests_logs_and_reraises_unhandled_exceptions(
    caplog: pytest.LogCaptureFixture,
) -> None:
    async def call_next(request: Request):
        raise ValueError("boom")

    async def run() -> None:
        await log_requests(_fake_request(), call_next)

    with caplog.at_level(logging.ERROR, logger="api.main"):
        with pytest.raises(ValueError):
            asyncio.run(run())

    assert any("unhandled exception" in record.message for record in caplog.records)
