# email-automation

A professional Python library and CLI for sending personalized bulk emails via SMTP.

## Installation

```bash
# From the repo root
pip install .

# Or in editable/dev mode
pip install -e ".[dev]"
```

## Quick Start

### CLI

```bash
# Create a .env config interactively
email-automation init

# Test your SMTP connection
email-automation test

# Preview contacts from a CSV
email-automation preview contacts.csv

# Dry-run (no emails sent)
email-automation send contacts.csv --test-mode

# Send for real
email-automation send contacts.csv --live --resume resume.pdf
```

### Python API

```python
from email_automation import Settings, EmailCampaign, CampaignConfig

settings = Settings()  # loads from .env / environment
campaign = EmailCampaign(settings)

result = campaign.run(
    CampaignConfig(csv_path="contacts.csv", test_mode=True)
)

print(f"Sent {result.sent}/{result.total}")
```

## Configuration

All settings are read from environment variables prefixed with `EA_`. You can
also place them in a `.env` file in your working directory.

| Variable | Required | Default | Description |
|---|---|---|---|
| `EA_SMTP_USERNAME` | yes | — | SMTP login username |
| `EA_SMTP_PASSWORD` | yes | — | SMTP password / app password |
| `EA_SENDER_NAME` | yes | — | Display name on outgoing emails |
| `EA_SENDER_EMAIL` | yes | — | Sender email address |
| `EA_SMTP_HOST` | no | `smtp.gmail.com` | SMTP server hostname |
| `EA_SMTP_PORT` | no | `587` | SMTP server port |
| `EA_EMAIL_DELAY_SECONDS` | no | `2.0` | Pause between emails (seconds) |
| `EA_LOG_LEVEL` | no | `INFO` | Python log level |

See `.env.example` for a template.

## CSV Format

Your contacts CSV must contain these columns:

| Column | Required | Description |
|---|---|---|
| `company_name` | yes | Company name |
| `role` | yes | Job title / role |
| `recruiter_email` | yes | Recipient email address |
| `recruiter_first_name` | no | Personalised greeting name |

## CLI Reference

| Command | Description |
|---|---|
| `email-automation init` | Interactively create a `.env` file |
| `email-automation test` | Test the SMTP connection |
| `email-automation preview <csv>` | Show contacts table and sample email |
| `email-automation send <csv>` | Run a campaign (`--test-mode` / `--live`) |

Run `email-automation --help` for full option details.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
