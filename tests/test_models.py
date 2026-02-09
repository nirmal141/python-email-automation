from datetime import datetime, timezone

import pytest

from email_automation.models import CampaignResult, Contact


class TestContact:
    def test_valid_contact(self):
        c = Contact(
            company_name="Acme",
            role="Engineer",
            recruiter_email="alice@acme.com",
        )
        assert c.company_name == "Acme"
        assert c.recruiter_first_name is None

    def test_with_recruiter_name(self):
        c = Contact(
            company_name="Acme",
            role="Engineer",
            recruiter_email="alice@acme.com",
            recruiter_first_name="Alice",
        )
        assert c.recruiter_first_name == "Alice"

    def test_invalid_email_rejected(self):
        with pytest.raises(Exception):
            Contact(
                company_name="Acme",
                role="Engineer",
                recruiter_email="not-an-email",
            )

    def test_blank_company_rejected(self):
        with pytest.raises(Exception):
            Contact(
                company_name="   ",
                role="Engineer",
                recruiter_email="alice@acme.com",
            )

    def test_blank_role_rejected(self):
        with pytest.raises(Exception):
            Contact(
                company_name="Acme",
                role="",
                recruiter_email="alice@acme.com",
            )


class TestCampaignResult:
    def test_serialisation_roundtrip(self):
        now = datetime.now(tz=timezone.utc)
        r = CampaignResult(
            total=10,
            sent=8,
            failed=2,
            failed_emails=["x@y.com", "a@b.com"],
            duration_seconds=12.5,
            start_time=now,
            end_time=now,
        )
        data = r.model_dump()
        assert data["total"] == 10
        assert len(data["failed_emails"]) == 2

        r2 = CampaignResult.model_validate(data)
        assert r2 == r
