"""email-automation — Professional bulk email library and CLI."""

from .config import Settings
from .engine import EmailCampaign
from .models import CampaignConfig, CampaignResult, Contact, EmailContent, EmailTemplate
from .smtp import SMTPConnection

__all__ = [
    "CampaignConfig",
    "CampaignResult",
    "Contact",
    "EmailCampaign",
    "EmailContent",
    "EmailTemplate",
    "Settings",
    "SMTPConnection",
]
