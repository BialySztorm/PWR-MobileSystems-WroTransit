import logging

import pytest

import ingest.logging_config as logging_config


@pytest.fixture(autouse=True)
def _reset_logging_configured():
    logging_config._CONFIGURED = False
    yield
    logging_config._CONFIGURED = False


def test_configure_logging_falls_back_to_info_on_invalid_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LOG_LEVEL", "NOT_A_REAL_LEVEL")
    calls: list[dict] = []
    monkeypatch.setattr(logging, "basicConfig", lambda **kwargs: calls.append(kwargs))

    logging_config.configure_logging()  # must not raise

    assert calls == [
        {"level": "INFO", "format": "%(asctime)s %(levelname)s %(name)s %(message)s"}
    ]
