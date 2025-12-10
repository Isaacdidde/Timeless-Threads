"""
utils/email_service.py

Production-grade email sending utility with:
- Strict environment validation
- TLS/SSL support
- Safe failover
- Logging
"""

import os
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


logger = logging.getLogger(__name__)


def _get_env(name, default=None, required=False):
    """Fetch environment variable safely."""
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def send_email(to_email: str, subject: str, message_html: str) -> bool:
    """
    Send an HTML email with proper TLS/SSL support.

    Returns:
        True  → success  
        False → failure (logged)
    """

    try:
        # ----------------------------
        # Load & validate ENV config
        # ----------------------------
        email_user = _get_env("EMAIL_USER", required=True)
        email_pass = _get_env("EMAIL_PASS", required=True)
        email_host = _get_env("EMAIL_HOST", required=True)

        # Default to TLS port 587 if missing
        email_port = int(_get_env("EMAIL_PORT", 587))

        use_ssl = os.getenv("EMAIL_SSL", "false").lower() in ("1", "true", "yes")

        # ----------------------------
        # Build email message
        # ----------------------------
        msg = MIMEMultipart()
        msg["From"] = email_user
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(message_html, "html", "utf-8"))

        # ----------------------------
        # SMTP Connection
        # ----------------------------
        if use_ssl:
            # --- SSL MODE ---
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(email_host, email_port, context=context)
        else:
            # --- TLS MODE ---
            server = smtplib.SMTP(email_host, email_port, timeout=10)
            server.starttls(context=ssl.create_default_context())

        # Login & send
        server.login(email_user, email_pass)
        server.sendmail(email_user, to_email, msg.as_string())
        server.quit()

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Email sending failed → {e}")
        return False
