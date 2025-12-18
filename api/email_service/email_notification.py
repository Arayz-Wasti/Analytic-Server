import smtplib
from email.message import EmailMessage
from backend.utils.settings import Settings
import logging

settings = Settings()

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, message: str) -> None:
        try:
            msg = EmailMessage()
            msg["From"] = settings.SMTP_FROM
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.set_content(message)
            with smtplib.SMTP_SSL(
                settings.SMTP_HOST,
                settings.SMTP_PORT
            ) as server:
                server.login(
                    settings.SMTP_USERNAME,
                    settings.SMTP_PASSWORD
                )
                server.send_message(msg)
            logger.info("Email sent to %s", to_email)
        except Exception as e:
            logger.error("Email failed: %s", str(e))
            raise
