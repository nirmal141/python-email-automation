from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, EmailStr, field_validator


class Contact(BaseModel):
    """A single recipient parsed from a CSV row."""

    company_name: str
    role: str
    recruiter_email: EmailStr
    recruiter_first_name: str | None = None

    @field_validator("company_name", "role")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v.strip()


class EmailContent(BaseModel):
    """A fully rendered email ready to send."""

    subject: str
    html_body: str
    text_body: str


class EmailTemplate(BaseModel):
    """Configurable email template with placeholders."""

    subject_template: str = "Interest in {role} at {company_name}"
    body_template: str = (
        "Hi {recruiter_name},\n\n"
        "I'm reaching out to express my interest in the {role} role "
        "at {company_name}. I believe my background and projects align "
        "well with the position's requirements.\n\n"
        "I'd welcome the chance to share relevant work samples and "
        "discuss how I can contribute to the team."
    )
    signature: str = (
        "Best regards,\n{sender_name}\n{sender_email}"
    )


class CampaignConfig(BaseModel):
    """Configuration for a single campaign run."""

    csv_path: Path
    test_mode: bool = True
    delay_seconds: float = 2.0
    resume_path: Path | None = None

    @field_validator("csv_path")
    @classmethod
    def csv_must_exist(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"CSV file not found: {v}")
        return v

    @field_validator("resume_path")
    @classmethod
    def resume_must_exist_if_set(cls, v: Path | None) -> Path | None:
        if v is not None and not v.exists():
            raise ValueError(f"Resume file not found: {v}")
        return v


class CampaignResult(BaseModel):
    """Summary of a completed campaign."""

    total: int
    sent: int
    failed: int
    failed_emails: list[str] = []
    duration_seconds: float
    start_time: datetime
    end_time: datetime
