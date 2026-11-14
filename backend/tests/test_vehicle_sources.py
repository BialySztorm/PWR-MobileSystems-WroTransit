import ssl
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode

import httpx
import pytest

from ingest.sources import MpkSource, Recorder


class _FakeResponse:
    def __init__(self, payload: list[dict]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> list[dict]:
        return self._payload


def test_mpk_source_sends_typed_body_first(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[tuple[str, str]]] = []

    def fake_post(self: httpx.Client, url: str, content=None, headers=None) -> _FakeResponse:
        calls.append(parse_qsl(content))
        return _FakeResponse(
            [{"name": "4", "type": "tram", "x": 51.11, "y": 17.03, "k": 123}]
        )

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    source = MpkSource(tram_lines=["4"], bus_lines=["144"])
    readings = source.fetch()

    assert len(calls) == 1
    assert ("busList[tram][]", "4") in calls[0]
    assert ("busList[bus][]", "144") in calls[0]
    assert len(readings) == 1


def test_mpk_source_falls_back_to_untyped_body_on_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[tuple[str, str]]] = []

    def fake_post(self: httpx.Client, url: str, content=None, headers=None) -> _FakeResponse:
        calls.append(parse_qsl(content))
        if len(calls) == 1:
            return _FakeResponse([])
        return _FakeResponse(
            [{"name": "8", "type": "bus", "x": 51.1, "y": 17.0, "k": 999}]
        )

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    source = MpkSource(tram_lines=["4"], bus_lines=["8"])
    readings = source.fetch()

    assert len(calls) == 2
    assert all(key == "busList[][]" for key, _ in calls[1])
    assert len(readings) == 1
    assert readings[0].vehicle_id == "999"
    assert readings[0].vehicle_type == "bus"


def test_mpk_source_maps_fields_with_xy_swap_and_records(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    def fake_post(self: httpx.Client, url: str, content=None, headers=None) -> _FakeResponse:
        return _FakeResponse(
            [{"name": "31", "type": "tram", "x": 51.09238, "y": 17.01899, "k": 14482003}]
        )

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    recorder = Recorder(tmp_path)
    source = MpkSource(tram_lines=["31"], bus_lines=[], recorder=recorder)
    readings = source.fetch()

    assert len(readings) == 1
    reading = readings[0]
    assert reading.vehicle_id == "14482003"
    assert reading.line == "31"
    assert reading.vehicle_type == "tram"
    assert reading.lat == 51.09238
    assert reading.lon == 17.01899

    recorded_files = list(tmp_path.glob("*.jsonl"))
    assert len(recorded_files) == 1


def test_mpk_source_returns_empty_on_request_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(self: httpx.Client, url: str, content=None, headers=None):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    source = MpkSource(tram_lines=["4"], bus_lines=[])

    assert source.fetch() == []


def test_mpk_source_reraises_tls_verification_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(self: httpx.Client, url: str, content=None, headers=None):
        raise httpx.ConnectError("certificate verify failed: self signed certificate")

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    source = MpkSource(tram_lines=["4"], bus_lines=[])

    with pytest.raises(httpx.ConnectError):
        source.fetch()


def test_mpk_source_reraises_tls_failure_even_without_the_exact_message_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Different OpenSSL/platform builds phrase a cert failure differently - the real
    signal is the wrapped ssl.SSLCertVerificationError, not a fixed message substring."""

    def fake_post(self: httpx.Client, url: str, content=None, headers=None):
        try:
            raise ssl.SSLCertVerificationError("some platform-specific wording")
        except ssl.SSLCertVerificationError as ssl_exc:
            raise httpx.ConnectError("unrelated-looking wrapper message") from ssl_exc

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    source = MpkSource(tram_lines=["4"], bus_lines=[])

    with pytest.raises(httpx.ConnectError):
        source.fetch()


def test_recorder_prunes_recordings_older_than_retention(tmp_path) -> None:
    now = datetime(2026, 1, 10, tzinfo=timezone.utc)
    old_path = tmp_path / "vehicle_positions_20260101.jsonl"
    old_path.write_text('{"recorded_at": "2026-01-01T00:00:00+00:00", "raw": []}\n')

    recorder = Recorder(tmp_path, retention_days=7)
    recorder.record([{"name": "4", "type": "tram", "x": 1.0, "y": 2.0, "k": 1}], now)

    assert not old_path.exists()
    assert (tmp_path / "vehicle_positions_20260110.jsonl").exists()


def test_repeated_key_body_round_trips_through_real_httpx() -> None:
    """Regression test: httpx.Client.post(data=<list of tuples>) silently mis-encodes
    repeated-key form bodies (unlike `requests` - raises a TypeError deep in h11 when
    actually sent). MpkSource avoids `data=` entirely and urlencodes by hand into
    `content=`; this exercises that exact path against a real (mocked-transport) httpx
    client, with no monkeypatching of httpx itself."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = request.content
        captured["content_type"] = request.headers.get("content-type")
        return httpx.Response(200, json=[])

    body = [("busList[tram][]", "4"), ("busList[bus][]", "144")]
    encoded_body = urlencode(body)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        client.post(
            "https://mpk.wroc.pl/bus_position",
            content=encoded_body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    parsed = parse_qsl(captured["body"].decode())
    assert ("busList[tram][]", "4") in parsed
    assert ("busList[bus][]", "144") in parsed
    assert captured["content_type"] == "application/x-www-form-urlencoded"
