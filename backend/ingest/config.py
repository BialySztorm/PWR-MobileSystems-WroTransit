"""Vehicle-polling configuration, read from environment variables."""
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_RECORDINGS_DIR = Path(__file__).resolve().parent.parent / "data" / "recordings"


@dataclass(frozen=True)
class Config:
    source: str = "mpk"
    """"mpk" (live polling) or "replay" (play back a recording)."""
    poll_interval_s: float = 10.0
    http_timeout_s: float = 5.0
    recordings_dir: Path = DEFAULT_RECORDINGS_DIR
    replay_speed: float = 1.0
    replay_file: Path | None = None
    """Explicit recording to replay; defaults to the newest file in recordings_dir."""


def load_config() -> Config:
    recordings_dir = Path(os.environ.get("RECORDINGS_DIR", str(DEFAULT_RECORDINGS_DIR)))
    replay_file = os.environ.get("REPLAY_FILE")
    return Config(
        source=os.environ.get("SOURCE", "mpk"),
        poll_interval_s=float(os.environ.get("POLL_INTERVAL_S", "10")),
        http_timeout_s=float(os.environ.get("HTTP_TIMEOUT_S", "5")),
        recordings_dir=recordings_dir,
        replay_speed=float(os.environ.get("REPLAY_SPEED", "1.0")),
        replay_file=Path(replay_file) if replay_file else None,
    )
