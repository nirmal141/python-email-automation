import logging
import os
import time
from collections.abc import Callable
from datetime import datetime, timezone
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

import pandas as pd

from .config import Settings
from .models import (
    CampaignConfig,
    CampaignResult,
    Contact,
    EmailContent,
    EmailTemplate,
)
from .smtp import SMTPConnection

logger = logging.getLogger(__name__)


class EmailCampaign:
    """Core public API for building and sending email campaigns."""

    def __init__(
        self,
        settings: Settings,
        template: EmailTemplate | None = None,
    ) -> None:
        self.settings = settings
        self.template = template or EmailTemplate()

    # ------------------------------------------------------------------
    # Contact loading
    # ------------------------------------------------------------------

    def load_contacts(self, csv_path: Path) -> list[Contact]:
        """Read and validate contacts from a CSV file."""
        df = pd.read_csv(csv_path)

        required = {"company_name", "role", "recruiter_email"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")

        contacts: list[Contact] = []
        for idx, row in df.iterrows():
            first_name = row.get("recruiter_first_name")
            if pd.isna(first_name) or (isinstance(first_name, str) and not first_name.strip()):
                first_name = None
            contacts.append(
                Contact(
                    company_name=row["company_name"],
                    role=row["role"],
                    recruiter_email=row["recruiter_email"],
                    recruiter_first_name=first_name,
                )
            )
        return contacts

    # ------------------------------------------------------------------
    # Email creation
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_name(email: str) -> str:
        """Derive a display name from an email local-part."""
        local = email.split("@")[0]
        for sep in (".", "_"):
            if sep in local:
                return " ".join(part.capitalize() for part in local.split(sep))
        return local.capitalize()

    def create_email(self, contact: Contact) -> EmailContent:
        """Render a personalised email for *contact*."""
        recruiter_name = (
            contact.recruiter_first_name
            if contact.recruiter_first_name
            else self._extract_name(contact.recruiter_email)
        )

        fmt = dict(
            recruiter_name=recruiter_name,
            company_name=contact.company_name,
            role=contact.role,
            sender_name=self.settings.sender_name,
            sender_email=self.settings.sender_email,
        )

        subject = self.template.subject_template.format(**fmt)
        body_text = self.template.body_template.format(**fmt)
        signature = self.template.signature.format(**fmt)

        text_body = f"{body_text}\n\n{signature}"

        html_body = (
            "<html><body style='margin:0;padding:0;'>"
            "<div style='font-family:Arial,Helvetica,sans-serif;"
            "font-size:14px;line-height:1.45;color:#111;'>"
        )
        for paragraph in body_text.split("\n\n"):
            html_body += f"<p style='margin:0 0 8px;'>{paragraph}</p>"
        sig_html = signature.replace("\n", "<br>")
        html_body += f"<p style='margin:0 0 8px;'>{sig_html}</p>"
        html_body += "</div></body></html>"

        return EmailContent(subject=subject, html_body=html_body, text_body=text_body)

    # ------------------------------------------------------------------
    # Sending
    # ------------------------------------------------------------------

    def send_email(
        self,
        contact: Contact,
        content: EmailContent,
        smtp_server: "smtplib.SMTP",
        resume_path: Path | None = None,
    ) -> bool:
        """Send a single email via an already-connected SMTP server."""
        import smtplib as _smtplib  # noqa: F811 – used only for type clarity

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = formataddr(
                (self.settings.sender_name, self.settings.sender_email)
            )
            msg["To"] = contact.recruiter_email
            msg["Subject"] = content.subject

            msg.attach(MIMEText(content.text_body, "plain"))
            msg.attach(MIMEText(content.html_body, "html"))

            if resume_path and resume_path.exists():
                with open(resume_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={resume_path.name}",
                    )
                    msg.attach(part)

            smtp_server.send_message(msg)
            logger.info("Sent email to %s", contact.recruiter_email)
            return True
        except Exception as exc:
            logger.error("Failed to send to %s: %s", contact.recruiter_email, exc)
            return False

    # ------------------------------------------------------------------
    # Campaign orchestration
    # ------------------------------------------------------------------

    def run(
        self,
        config: CampaignConfig,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> CampaignResult:
        """Execute a full campaign described by *config*."""
        contacts = self.load_contacts(config.csv_path)
        total = len(contacts)
        sent = 0
        failed = 0
        failed_emails: list[str] = []

        start = datetime.now(tz=timezone.utc)

        if config.test_mode:
            for i, contact in enumerate(contacts):
                content = self.create_email(contact)
                logger.info(
                    "TEST MODE — Would send to %s (%s – %s) | Subject: %s",
                    contact.recruiter_email,
                    contact.company_name,
                    contact.role,
                    content.subject,
                )
                sent += 1
                if on_progress:
                    on_progress(i + 1, total)
        else:
            with SMTPConnection(self.settings) as server:
                for i, contact in enumerate(contacts):
                    content = self.create_email(contact)
                    if self.send_email(contact, content, server, config.resume_path):
                        sent += 1
                    else:
                        failed += 1
                        failed_emails.append(contact.recruiter_email)
                    if on_progress:
                        on_progress(i + 1, total)
                    if i < total - 1:
                        time.sleep(config.delay_seconds)

        end = datetime.now(tz=timezone.utc)

        result = CampaignResult(
            total=total,
            sent=sent,
            failed=failed,
            failed_emails=failed_emails,
            duration_seconds=(end - start).total_seconds(),
            start_time=start,
            end_time=end,
        )
        logger.info(
            "Campaign complete: %d sent, %d failed out of %d (%.1fs)",
            sent,
            failed,
            total,
            result.duration_seconds,
        )
        return result

    def send_test(self, to_email: str) -> bool:
        """Send a single test email to *to_email*."""
        contact = Contact(
            company_name="Test Company",
            role="Test Role",
            recruiter_email=to_email,
            recruiter_first_name="Test",
        )
        content = self.create_email(contact)
        with SMTPConnection(self.settings) as server:
            return self.send_email(contact, content, server)
