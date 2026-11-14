import json
from datetime import datetime, timedelta, timezone

import pytest

from ingest.sources import MAX_REPLAY_GAP_S, ReplaySource


def test_replay_source_plays_back_recorded_entries_in_order(tmp_path) -> None:
    path = tmp_path / "vehicle_positions_20260101.jsonl"
    t0 = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=10)
    entries = [
        {
            "recorded_at": t0.isoformat(),
            "raw": [{"name": "4", "type": "tram", "x": 51.1, "y": 17.0, "k": 1}],
        },
        {
            "recorded_at": t1.isoformat(),
            "raw": [{"name": "4", "type": "tram", "x": 51.2, "y": 17.1, "k": 1}],
        },
    ]
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")

    source = ReplaySource(recordings_dir=tmp_path, replay_file=path, speed=1000)

    first = source.fetch()
    second = source.fetch()

    assert first[0].lat == 51.1
    assert second[0].lat == 51.2


def test_replay_source_caps_a_huge_gap_instead_of_blocking_for_hours(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "vehicle_positions_20260101.jsonl"
    t0 = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(hours=6)  # an overnight-sized gap in the recording
    entries = [
        {
            "recorded_at": t0.isoformat(),
            "raw": [{"name": "4", "type": "tram", "x": 51.1, "y": 17.0, "k": 1}],
        },
        {
            "recorded_at": t1.isoformat(),
            "raw": [{"name": "4", "type": "tram", "x": 51.2, "y": 17.1, "k": 1}],
        },
    ]
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")

    sleep_calls: list[float] = []
    monkeypatch.setattr("ingest.sources.time.sleep", lambda s: sleep_calls.append(s))

    source = ReplaySource(recordings_dir=tmp_path, replay_file=path, speed=1)
    source.fetch()
    source.fetch()

    assert sleep_calls == [MAX_REPLAY_GAP_S]


def test_replay_source_loops_back_to_start_when_exhausted(tmp_path) -> None:
    path = tmp_path / "vehicle_positions_20260101.jsonl"
    entry = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "raw": [{"name": "4", "type": "tram", "x": 51.1, "y": 17.0, "k": 1}],
    }
    path.write_text(json.dumps(entry) + "\n", encoding="utf-8")

    source = ReplaySource(recordings_dir=tmp_path, replay_file=path, speed=1000)

    first = source.fetch()
    second = source.fetch()

    assert first[0].vehicle_id == second[0].vehicle_id == "1"
