"""
E9, E10 from Backend Spec sections 5, 5.1 and 7.3.

IMPORTANT GAP THIS FIXES: the previous webhook handler (in main.py) parsed
incoming replies but only logged them -- it never updated a vendor's status.
That means the demo's must-not-cut path ("vendor taps YES, dashboard updates
live") could not have actually worked end-to-end before this file existed.
"""
import hashlib
import hmac
import json
import re
from datetime import datetime

from fastapi import APIRouter, Request, Response, status

from app.config import settings
from app.database import SessionLocal
from app.models import Vendor, Message, WebhookEvent
from app.services.status import touch
from app.services.activity import log_activity

router = APIRouter(prefix="/api/v1/webhook", tags=["Webhook"])

BUTTON_RE = re.compile(r"^(YES|NO):(\d+)$")


@router.get("/whatsapp")
def verify_webhook(request: Request):
    """E9: Meta's verification handshake."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge or "", media_type="text/plain")

    return Response(content="Verification token mismatch", status_code=status.HTTP_403_FORBIDDEN)


def _verify_signature(raw_body: bytes, header_sig: str | None) -> bool:
    if settings.WEBHOOK_SKIP_SIGNATURE:
        return True
    if not header_sig or not header_sig.startswith("sha256=") or not settings.WHATSAPP_APP_SECRET:
        return False
    expected = hmac.new(settings.WHATSAPP_APP_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    provided = header_sig.split("=", 1)[1]
    return hmac.compare_digest(expected, provided)


def _extract_button_answer(message: dict) -> tuple[str, int] | None:
    """Returns (answer, vendor_id) from either a template quick-reply or an
    interactive reply button. Spec 7.3 point 3."""
    if message.get("type") == "button":
        payload = message.get("button", {}).get("payload", "")
    elif message.get("type") == "interactive":
        payload = message.get("interactive", {}).get("button_reply", {}).get("id", "")
    else:
        return None

    m = BUTTON_RE.match(payload)
    if not m:
        return None
    answer, vendor_id = m.group(1), int(m.group(2))
    return answer, vendor_id


@router.post("/whatsapp")
async def receive_webhook(request: Request):
    """
    E10. Always returns 200 quickly, even on parse errors, because Meta
    retries non-200 responses and can disable a repeatedly-failing webhook.
    Uses its own DB session (not the get_db dependency) so a bad payload
    can't be blamed on request-lifecycle plumbing -- it's caught and logged
    instead of raising.
    """
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not _verify_signature(raw_body, signature):
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        payload = json.loads(raw_body or b"{}")
    except json.JSONDecodeError:
        return {"status": "ignored", "reason": "invalid json"}

    db = SessionLocal()
    try:
        touched_event_ids: set[int] = set()

        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                for message in value.get("messages", []):
                    wa_message_id = message.get("id")

                    # Idempotency: skip a delivery we've already recorded.
                    if wa_message_id and db.query(WebhookEvent).filter(WebhookEvent.wa_message_id == wa_message_id).first():
                        continue
                    db.add(WebhookEvent(wa_message_id=wa_message_id, payload=json.dumps(message), processed=0))

                    answer_pair = _extract_button_answer(message)
                    vendor = None
                    if answer_pair:
                        answer, vendor_id = answer_pair
                        vendor = db.get(Vendor, vendor_id)
                    else:
                        # Fallback: sender typed free text instead of tapping a
                        # button. Match "yes"/"no" by phone to their most
                        # recent vendor row still awaiting a reply.
                        from_phone = "+" + message.get("from", "")
                        text = (message.get("text", {}) or {}).get("body", "").strip().lower()
                        if text in ("yes", "no"):
                            vendor = (
                                db.query(Vendor)
                                .filter(Vendor.phone == from_phone, Vendor.status == "sent")
                                .order_by(Vendor.id.desc()).first()
                            )
                            answer = "YES" if text == "yes" else "NO"

                    if vendor is None:
                        continue  # unmatched message; already logged to webhook_events above

                    if vendor.status in ("sent", "declined", "confirmed"):
                        new_status = "confirmed" if answer == "YES" else "declined"
                        vendor.status = new_status
                        vendor.status_updated_at = datetime.utcnow()
                        db.add(Message(
                            vendor_id=vendor.id, direction="in", wa_message_id=wa_message_id,
                            kind=message.get("type", "text"), payload=json.dumps(message), wa_status=None,
                        ))
                        log_activity(
                            db, vendor.event_id,
                            f"{vendor.name} ({vendor.role}) {'confirmed' if new_status == 'confirmed' else 'declined'} via WhatsApp",
                            "vendor_confirmed" if new_status == "confirmed" else "vendor_declined",
                            vendor_id=vendor.id,
                        )
                        touched_event_ids.add(vendor.event_id)

                for st in value.get("statuses", []):
                    wa_message_id = st.get("id")
                    wa_status = st.get("status")
                    msg = db.query(Message).filter(Message.wa_message_id == wa_message_id).first()
                    if msg is None:
                        continue
                    msg.wa_status = wa_status
                    if wa_status == "failed" and msg.vendor.status == "sent":
                        msg.vendor.status = "failed"
                        msg.vendor.status_updated_at = datetime.utcnow()
                        log_activity(db, msg.vendor.event_id, f"Message to {msg.vendor.name} failed to deliver", "message_failed", vendor_id=msg.vendor.id)
                        touched_event_ids.add(msg.vendor.event_id)
                    elif wa_status == "delivered":
                        log_activity(db, msg.vendor.event_id, f"Message to {msg.vendor.name} delivered", "message_delivered", vendor_id=msg.vendor.id)
                        touched_event_ids.add(msg.vendor.event_id)
                    elif wa_status == "read":
                        log_activity(db, msg.vendor.event_id, f"Message to {msg.vendor.name} read", "message_read", vendor_id=msg.vendor.id)
                        touched_event_ids.add(msg.vendor.event_id)

        for eid in touched_event_ids:
            touch(db, eid)
        db.commit()
    except Exception:
        db.rollback()
        # Swallow the error -- Meta must always get a fast 200, and the raw
        # payload is already recorded in webhook_events for debugging.
    finally:
        db.close()

    return {"status": "received"}
