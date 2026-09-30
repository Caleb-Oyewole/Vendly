"""
Section 7 (WhatsApp integration). Sends either:
  - "template" mode: the approved vendor_booking_confirm template (7.2), or
  - "interactive" mode: a plain reply-button message, which only lands inside
    the 24h customer-service window but needs no Meta template approval.
Both use quick-reply ids in the exact "YES:{vendor_id}" / "NO:{vendor_id}"
format the webhook parser (routers/webhook.py) expects -- switching modes
never requires touching the webhook code, per spec 7.3.
"""
from abc import ABC, abstractmethod
import logging

import requests

from app.config import settings
from app.models import Vendor

logger = logging.getLogger("uvicorn")


def _template_payload(vendor: Vendor, event) -> dict:
    return {
        "messaging_product": "whatsapp",
        "to": vendor.phone.lstrip("+"),
        "type": "template",
        "template": {
            "name": settings.WHATSAPP_TEMPLATE_NAME,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": vendor.name},
                        {"type": "text", "text": vendor.role},
                        {"type": "text", "text": event.name},
                        {"type": "text", "text": event.event_date.strftime("%a %d %b %Y")},
                        {"type": "text", "text": vendor.arrival_time},
                        {"type": "text", "text": event.venue},
                    ],
                },
                {
                    "type": "button", "sub_type": "quick_reply", "index": "0",
                    "parameters": [{"type": "payload", "payload": f"YES:{vendor.id}"}],
                },
                {
                    "type": "button", "sub_type": "quick_reply", "index": "1",
                    "parameters": [{"type": "payload", "payload": f"NO:{vendor.id}"}],
                },
            ],
        },
    }


def _interactive_payload(vendor: Vendor, event) -> dict:
    body = (
        f"Hi {vendor.name}, you're booked as {vendor.role} for {event.name} on "
        f"{event.event_date.strftime('%a %d %b %Y')}. Arrival: {vendor.arrival_time} "
        f"at {event.venue}. Can you confirm?"
    )
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": vendor.phone.lstrip("+"),
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": f"YES:{vendor.id}", "title": "Yes, I'm in"}},
                    {"type": "reply", "reply": {"id": f"NO:{vendor.id}", "title": "No, can't make it"}},
                ]
            },
        },
    }


def build_payload(vendor: Vendor, event) -> dict:
    return _template_payload(vendor, event) if settings.WHATSAPP_MODE == "template" else _interactive_payload(vendor, event)


class WhatsAppClient(ABC):
    @abstractmethod
    def send_confirmation(self, vendor: Vendor, event) -> dict:
        """Returns {"ok": bool, "wa_message_id": str|None, "error": str|None}."""
        raise NotImplementedError


class MetaWhatsAppClient(WhatsAppClient):
    def send_confirmation(self, vendor: Vendor, event) -> dict:
        url = f"https://graph.facebook.com/{settings.GRAPH_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = build_payload(vendor, event)
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=5)
            data = resp.json()
        except requests.RequestException as exc:
            return {"ok": False, "wa_message_id": None, "error": str(exc)}

        if resp.status_code >= 400:
            return {"ok": False, "wa_message_id": None, "error": data.get("error", data)}

        wa_id = (data.get("messages") or [{}])[0].get("id")
        return {"ok": True, "wa_message_id": wa_id, "error": None}


class MockWhatsAppClient(WhatsAppClient):
    """Simulates a vendor immediately tapping YES, by posting a Meta-shaped
    webhook body back to this app's own webhook endpoint."""

    def send_confirmation(self, vendor: Vendor, event) -> dict:
        logger.info(f"[MOCK WHATSAPP] Sending to {vendor.name} ({vendor.phone}) for '{event.name}'.")
        fake_message_id = f"mock.wamid.{vendor.id}.{int(event.version)}"

        fake_webhook_body = {
            "object": "whatsapp_business_account",
            "entry": [{"changes": [{"field": "messages", "value": {
                "messages": [{
                    "from": vendor.phone.lstrip("+"),
                    "id": f"mock.reply.{vendor.id}",
                    "type": "button",
                    "button": {"payload": f"YES:{vendor.id}", "text": "Yes, I'm in"},
                }],
                "statuses": [{"id": fake_message_id, "status": "delivered", "recipient_id": vendor.phone.lstrip("+")}],
            }}]}],
        }
        try:
            requests.post(settings.LOCAL_WEBHOOK_URL, json=fake_webhook_body, timeout=5)
            logger.info(f"[MOCK WHATSAPP] Delivered simulated webhook to {settings.LOCAL_WEBHOOK_URL}")
        except requests.RequestException as err:
            logger.warning(f"[MOCK WHATSAPP] Could not deliver mock webhook: {err}")

        return {"ok": True, "wa_message_id": fake_message_id, "error": None}


def get_whatsapp_client() -> WhatsAppClient:
    return MockWhatsAppClient() if settings.USE_MOCK_WHATSAPP else MetaWhatsAppClient()
