from abc import ABC, abstractmethod
import logging
import requests
from app.config import settings

logger = logging.getLogger("uvicorn")


class WhatsAppClient(ABC):
    """Abstract interface for sending WhatsApp notification messages."""

    @abstractmethod
    def send_template(
        self, phone_number: str, vendor_name: str, event_title: str, vendor_id: int
    ) -> dict:
        pass


class MetaWhatsAppClient(WhatsAppClient):
    """Real implementation making HTTP POST requests to Meta WhatsApp Cloud API."""

    def send_template(
        self, phone_number: str, vendor_name: str, event_title: str, vendor_id: int
    ) -> dict:
        url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Hello {vendor_name}, are you available for {event_title}?"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": f"ACCEPTED_{vendor_id}",
                                "title": "Accept",
                            },
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": f"DECLINED_{vendor_id}",
                                "title": "Decline",
                            },
                        },
                    ]
                },
            },
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.json()


class MockWhatsAppClient(WhatsAppClient):
    """Mock implementation for offline testing and immediate webhook simulation."""

    def send_template(
        self, phone_number: str, vendor_name: str, event_title: str, vendor_id: int
    ) -> dict:
        logger.info(
            f"[MOCK WHATSAPP] Outgoing message triggered for {vendor_name} ({phone_number}) for event '{event_title}'."
        )

        fake_webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": phone_number,
                                        "type": "interactive",
                                        "interactive": {
                                            "button_reply": {
                                                "id": f"ACCEPTED_{vendor_id}",
                                                "title": "Accept",
                                            }
                                        },
                                    }
                                ]
                            }
                        }
                    ]
                }
            ],
        }

        try:
            requests.post(
                settings.LOCAL_WEBHOOK_URL, json=fake_webhook_payload, timeout=5
            )
            logger.info(
                f"[MOCK WHATSAPP] Delivered simulated webhook to {settings.LOCAL_WEBHOOK_URL}"
            )
        except Exception as err:
            logger.warning(
                f"[MOCK WHATSAPP] Could not deliver mock webhook: {err}"
            )

        return {"status": "success", "mode": "mock", "vendor_id": vendor_id}


def get_whatsapp_client() -> WhatsAppClient:
    """Dependency provider returning Mock or Meta client depending on settings."""
    if settings.USE_MOCK_WHATSAPP:
        return MockWhatsAppClient()
    return MetaWhatsAppClient()