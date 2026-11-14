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


def _env_float(name: str, default: float) -> float:
    # os.environ.get(name, default) would not apply the default for a variable that is
    # set but empty (e.g. a half-filled `.env` line) - treat that the same as unset.
    value = os.environ.get(name)
    return float(value) if value else default


def load_config() -> Config:
    recordings_dir = Path(os.environ.get("RECORDINGS_DIR") or str(DEFAULT_RECORDINGS_DIR))
    replay_file = os.environ.get("REPLAY_FILE")
    return Config(
        source=os.environ.get("SOURCE") or "mpk",
        poll_interval_s=_env_float("POLL_INTERVAL_S", 10.0),
        http_timeout_s=_env_float("HTTP_TIMEOUT_S", 5.0),
        recordings_dir=recordings_dir,
        replay_speed=_env_float("REPLAY_SPEED", 1.0),
        replay_file=Path(replay_file) if replay_file else None,
    )
