import csv
import os
from pathlib import Path

import pytest

from email_automation.config import Settings
from email_automation.engine import EmailCampaign
from email_automation.models import CampaignConfig, Contact


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for key in list(os.environ):
        if key.startswith("EA_"):
            monkeypatch.delenv(key, raising=False)


@pytest.fixture()
def settings(monkeypatch):
    monkeypatch.setenv("EA_SMTP_USERNAME", "user@example.com")
    monkeypatch.setenv("EA_SMTP_PASSWORD", "secret")
    monkeypatch.setenv("EA_SENDER_NAME", "Test Sender")
    monkeypatch.setenv("EA_SENDER_EMAIL", "user@example.com")
    return Settings(_env_file=None)  # type: ignore[call-arg]


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "contacts.csv"
    with open(p, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["company_name", "role", "recruiter_email", "recruiter_first_name"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "company_name": "Acme",
                "role": "Engineer",
                "recruiter_email": "alice@acme.com",
                "recruiter_first_name": "Alice",
            }
        )
        writer.writerow(
            {
                "company_name": "Globex",
                "role": "Designer",
                "recruiter_email": "bob@globex.com",
                "recruiter_first_name": "",
            }
        )
    return p


class TestLoadContacts:
    def test_loads_valid_csv(self, settings, sample_csv):
        campaign = EmailCampaign(settings)
        contacts = campaign.load_contacts(sample_csv)
        assert len(contacts) == 2
        assert contacts[0].company_name == "Acme"

    def test_missing_column_raises(self, settings, tmp_path):
        bad = tmp_path / "bad.csv"
        bad.write_text("name,email\nAcme,alice@acme.com\n")
        campaign = EmailCampaign(settings)
        with pytest.raises(ValueError, match="missing required columns"):
            campaign.load_contacts(bad)


class TestCreateEmail:
    def test_personalises_subject(self, settings):
        campaign = EmailCampaign(settings)
        contact = Contact(
            company_name="Acme",
            role="Engineer",
            recruiter_email="alice@acme.com",
            recruiter_first_name="Alice",
        )
        content = campaign.create_email(contact)
        assert "Acme" in content.subject
        assert "Engineer" in content.subject

    def test_uses_extracted_name_when_no_first_name(self, settings):
        campaign = EmailCampaign(settings)
        contact = Contact(
            company_name="Acme",
            role="Engineer",
            recruiter_email="jane.doe@acme.com",
        )
        content = campaign.create_email(contact)
        assert "Jane Doe" in content.text_body


class TestRun:
    def test_test_mode_sends_none(self, settings, sample_csv):
        campaign = EmailCampaign(settings)
        config = CampaignConfig(csv_path=sample_csv, test_mode=True)
        result = campaign.run(config)
        assert result.total == 2
        assert result.sent == 2
        assert result.failed == 0
