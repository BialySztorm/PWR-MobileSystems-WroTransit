"""Vehicle position sources.

Wrocław does not publish GTFS-Realtime; the only live feed is MPK's own (undocumented,
unstable) map endpoint. Access to it is isolated behind `VehiclePositionSource` so it can
be swapped or mocked, and every raw response is recorded to disk so a `ReplaySource` can
reproduce a session later for tests/demo without hitting the network.
"""
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

import httpx

from ingest.config import Config

logger = logging.getLogger(__name__)

MPK_URL = "https://mpk.wroc.pl/bus_position"


@dataclass(frozen=True)
class VehicleReading:
    vehicle_id: str
    line: str
    vehicle_type: str
    """"tram" or "bus"."""
    lat: float
    lon: float
    recorded_at: datetime


class VehiclePositionSource(Protocol):
    def fetch(self) -> list[VehicleReading]: ...


def _parse_raw(raw: list[dict], recorded_at: datetime) -> list[VehicleReading]:
    readings = []
    for entry in raw:
        try:
            readings.append(
                VehicleReading(
                    vehicle_id=str(entry["k"]),
                    line=str(entry["name"]),
                    vehicle_type=entry["type"],
                    lat=float(entry["x"]),
                    lon=float(entry["y"]),
                    recorded_at=recorded_at,
                )
            )
        except (KeyError, TypeError, ValueError):
            logger.warning("Skipping malformed vehicle position entry: %r", entry)
    return readings


class Recorder:
    """Appends every raw MPK response to a dated JSONL file for later replay."""

    def __init__(self, recordings_dir: Path) -> None:
        self._recordings_dir = recordings_dir

    def record(self, raw: list[dict], timestamp: datetime) -> None:
        self._recordings_dir.mkdir(parents=True, exist_ok=True)
        path = self._recordings_dir / f"vehicle_positions_{timestamp:%Y%m%d}.jsonl"
        line = json.dumps({"recorded_at": timestamp.isoformat(), "raw": raw})
        with path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


class MpkSource:
    """Polls MPK Wrocław's bus_position endpoint (see docs/Specifications.md section 2)."""

    def __init__(
        self,
        tram_lines: list[str],
        bus_lines: list[str],
        timeout_s: float = 5.0,
        recorder: Recorder | None = None,
    ) -> None:
        self._tram_lines = tram_lines
        self._bus_lines = bus_lines
        self._timeout_s = timeout_s
        self._recorder = recorder

    def _post(self, body: list[tuple[str, str]]) -> list[dict] | None:
        try:
            with httpx.Client(timeout=self._timeout_s) as client:
                response = client.post(MPK_URL, data=body)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as exc:
            if "certificate verify failed" in str(exc).lower():
                raise
            logger.warning("MPK request failed: %s", exc)
            return None
        except httpx.HTTPError as exc:
            logger.warning("MPK request failed: %s", exc)
            return None
        except ValueError:
            logger.warning("MPK response was not valid JSON")
            return None

    def fetch(self) -> list[VehicleReading]:
        typed_body = [("busList[tram][]", line) for line in self._tram_lines] + [
            ("busList[bus][]", line) for line in self._bus_lines
        ]
        raw = self._post(typed_body)

        if not raw:
            untyped_body = [
                ("busList[][]", line) for line in (*self._tram_lines, *self._bus_lines)
            ]
            raw = self._post(untyped_body)

        if not raw:
            return []

        now = datetime.now(timezone.utc)
        if self._recorder is not None:
            self._recorder.record(raw, now)
        return _parse_raw(raw, now)


class ReplaySource:
    """Replays a recorded JSONL session, preserving the original gaps between reads."""

    def __init__(self, recordings_dir: Path, replay_file: Path | None, speed: float = 1.0) -> None:
        path = replay_file or self._latest_recording(recordings_dir)
        self._entries = self._load(path)
        self._speed = speed
        self._index = 0
        self._last_recorded_at: datetime | None = None

    @staticmethod
    def _latest_recording(recordings_dir: Path) -> Path:
        files = sorted(recordings_dir.glob("vehicle_positions_*.jsonl"))
        if not files:
            raise FileNotFoundError(f"No recordings found in {recordings_dir}")
        return files[-1]

    @staticmethod
    def _load(path: Path) -> list[dict]:
        with path.open(encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def fetch(self) -> list[VehicleReading]:
        if self._index >= len(self._entries):
            logger.info("Replay exhausted, looping back to the start")
            self._index = 0
            self._last_recorded_at = None

        entry = self._entries[self._index]
        self._index += 1
        recorded_at = datetime.fromisoformat(entry["recorded_at"])

        if self._last_recorded_at is not None and self._speed > 0:
            gap_s = (recorded_at - self._last_recorded_at).total_seconds() / self._speed
            if gap_s > 0:
                time.sleep(gap_s)
        self._last_recorded_at = recorded_at

        return _parse_raw(entry["raw"], recorded_at)


def build_mpk_source(config: Config, tram_lines: list[str], bus_lines: list[str]) -> MpkSource:
    return MpkSource(
        tram_lines=tram_lines,
        bus_lines=bus_lines,
        timeout_s=config.http_timeout_s,
        recorder=Recorder(config.recordings_dir),
    )


def build_replay_source(config: Config) -> ReplaySource:
    return ReplaySource(
        recordings_dir=config.recordings_dir,
        replay_file=config.replay_file,
        speed=config.replay_speed,
    )
