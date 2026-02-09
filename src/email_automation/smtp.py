import logging
import smtplib
from types import TracebackType

from .config import Settings

logger = logging.getLogger(__name__)


class SMTPConnection:
    """Context manager for SMTP connections."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._server: smtplib.SMTP | None = None

    def __enter__(self) -> smtplib.SMTP:
        self._server = smtplib.SMTP(
            self._settings.smtp_host, self._settings.smtp_port
        )
        self._server.starttls()
        self._server.login(
            self._settings.smtp_username, self._settings.smtp_password
        )
        logger.info("Connected to SMTP server %s:%s", self._settings.smtp_host, self._settings.smtp_port)
        return self._server

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._server is not None:
            try:
                self._server.quit()
            except smtplib.SMTPException:
                pass
            self._server = None
            logger.info("Disconnected from SMTP server")

    def test_connection(self) -> bool:
        """Test whether SMTP credentials are valid."""
        try:
            with self:
                return True
        except Exception as exc:
            logger.error("SMTP connection test failed: %s", exc)
            return False
