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

    def fake_post(self: httpx.Client, url: str, data=None) -> _FakeResponse:
        calls.append(list(data))
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

    def fake_post(self: httpx.Client, url: str, data=None) -> _FakeResponse:
        calls.append(list(data))
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
    def fake_post(self: httpx.Client, url: str, data=None) -> _FakeResponse:
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
    def fake_post(self: httpx.Client, url: str, data=None):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    source = MpkSource(tram_lines=["4"], bus_lines=[])

    assert source.fetch() == []


def test_mpk_source_reraises_tls_verification_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(self: httpx.Client, url: str, data=None):
        raise httpx.ConnectError("certificate verify failed: self signed certificate")

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    source = MpkSource(tram_lines=["4"], bus_lines=[])

    with pytest.raises(httpx.ConnectError):
        source.fetch()
