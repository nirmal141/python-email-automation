from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables (prefixed with EA_)."""

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    sender_name: str
    sender_email: EmailStr
    email_delay_seconds: float = 2.0
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="EA_")
