import os

import pytest

from email_automation.config import Settings


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Remove any EA_ env vars that could leak into tests."""
    for key in list(os.environ):
        if key.startswith("EA_"):
            monkeypatch.delenv(key, raising=False)


def _base_env(monkeypatch, **overrides):
    defaults = {
        "EA_SMTP_USERNAME": "user@example.com",
        "EA_SMTP_PASSWORD": "secret",
        "EA_SENDER_NAME": "Test Sender",
        "EA_SENDER_EMAIL": "user@example.com",
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        monkeypatch.setenv(k, v)


class TestSettingsDefaults:
    def test_defaults_applied(self, monkeypatch):
        _base_env(monkeypatch)
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.smtp_host == "smtp.gmail.com"
        assert s.smtp_port == 587
        assert s.email_delay_seconds == 2.0
        assert s.log_level == "INFO"

    def test_required_fields_missing(self, monkeypatch):
        with pytest.raises(Exception):
            Settings(_env_file=None)  # type: ignore[call-arg]

    def test_custom_values(self, monkeypatch):
        _base_env(
            monkeypatch,
            EA_SMTP_HOST="mail.example.com",
            EA_SMTP_PORT="465",
            EA_EMAIL_DELAY_SECONDS="5.5",
        )
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.smtp_host == "mail.example.com"
        assert s.smtp_port == 465
        assert s.email_delay_seconds == 5.5
