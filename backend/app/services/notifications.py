"""Email/SMS notifications — wired for SendGrid, SMTP, Africa's Talking."""
from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, html: str) -> None:
    s = get_settings()
    if s.sendgrid_api_key:
        await _sendgrid(to, subject, html)
        return
    if s.smtp_host and s.smtp_user:
        await _smtp(to, subject, html)
        return
    logger.info("Email stub (no provider): to=%s subject=%s", to, subject)


async def _sendgrid(to: str, subject: str, html: str) -> None:
    s = get_settings()
    url = "https://api.sendgrid.com/v3/mail/send"
    body = {
        "personalizations": [{"to": [{"email": to}]}],
        "from": {"email": s.email_from},
        "subject": subject,
        "content": [{"type": "text/html", "value": html}],
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=body, headers={"Authorization": f"Bearer {s.sendgrid_api_key}"})
        r.raise_for_status()


async def _smtp(to: str, subject: str, html: str) -> None:
    import aiosmtplib
    from email.message import EmailMessage

    s = get_settings()
    msg = EmailMessage()
    msg["From"] = s.email_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content("HTML email", subtype="plain")
    msg.add_alternative(html, subtype="html")
    await aiosmtplib.send(
        msg,
        hostname=s.smtp_host,
        port=s.smtp_port,
        username=s.smtp_user,
        password=s.smtp_password,
        start_tls=True,
    )


async def send_sms(to_phone_e164: str, body: str) -> None:
    """Africa's Talking — Ethiopian numbers often +251XXXXXXXXX."""
    s = get_settings()
    if not (s.africastalking_username and s.africastalking_api_key):
        logger.info("SMS stub: to=%s body=%s", to_phone_e164, body[:80])
        return
    url = "https://api.africastalking.com/version1/messaging"
    data = {
        "username": s.africastalking_username,
        "to": to_phone_e164,
        "message": body[:480],
        "from": s.africastalking_sender_id or "JobET",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            url,
            data=data,
            headers={"apiKey": s.africastalking_api_key, "Accept": "application/json"},
        )
        r.raise_for_status()
