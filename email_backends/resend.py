import requests
import logging
from django.core.mail.backends.smtp import EmailBackend as GmailBackend
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gmail_backend = GmailBackend(
            host="smtp.gmail.com",
            port=587,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=True,
            fail_silently=self.fail_silently
        )

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent_count = 0

        for message in email_messages:
            use_gmail = message.extra_headers.get("X-Use-Gmail", False)

            if use_gmail:
                sent_count += self.gmail_backend.send_messages([message]) or 0
                continue

            try:
                sent = self._send_via_resend(message)
                if sent:
                    sent_count += 1
                else:
                    sent_count += self.gmail_backend.send_messages([message]) or 0
            except Exception as e:
                logger.error(f"Resend failed: {e}, falling back to Gmail")
                sent_count += self.gmail_backend.send_messages([message]) or 0

        return sent_count

    def _send_via_resend(self, message):
        api_key = settings.RESEND_API_KEY
        api_url = "https://api.resend.com/emails"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        plain_body = message.body
        html_body = None
        if hasattr(message, 'alternatives'):
            for alt, mimetype in message.alternatives:
                if mimetype == 'text/html':
                    html_body = alt

        payload = {
            "from": message.extra_headers.get("From", message.from_email or settings.DEFAULT_FROM_EMAIL),
            "to": message.to,
            "subject": message.subject,
        }

        if html_body:
            payload["html"] = html_body
        if plain_body:
            payload["text"] = plain_body

        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return True