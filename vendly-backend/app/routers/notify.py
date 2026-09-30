"""E8 from Backend Spec section 5 / 5.1."""
import json
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import NotFoundError
from app.models import Event, Vendor, Message
from app.schemas import NotifySendRequest
from app.services.whatsapp import WhatsAppClient, get_whatsapp_client, build_payload
from app.services.status import touch
from app.services.activity import log_activity

router = APIRouter(prefix="/api/v1/notify", tags=["Notification"])


@router.post("/send")
def send_notifications(
    payload: NotifySendRequest,
    db: Session = Depends(get_db),
    client: WhatsAppClient = Depends(get_whatsapp_client),
):
    """Sends the confirmation message to the requested vendors, or to every
    pending/failed vendor on the event if vendor_ids is omitted."""
    event = db.get(Event, payload.event_id)
    if event is None:
        raise NotFoundError(f"Event {payload.event_id} not found")

    query = db.query(Vendor).filter(Vendor.event_id == event.id)
    if payload.vendor_ids:
        query = query.filter(Vendor.id.in_(payload.vendor_ids))
    else:
        query = query.filter(Vendor.status.in_(["pending", "failed"]))
    vendors = query.all()

    results = []
    any_success = False
    for vendor in vendors:
        result = client.send_confirmation(vendor, event)
        sent_payload = build_payload(vendor, event)

        if result["ok"]:
            vendor.status = "sent"
            vendor.status_updated_at = datetime.utcnow()
            db.add(Message(
                vendor_id=vendor.id, direction="out", wa_message_id=result["wa_message_id"],
                kind=sent_payload["type"], payload=json.dumps(sent_payload), wa_status="accepted",
            ))
            log_activity(db, event.id, f"Message sent to {vendor.name} ({vendor.role})", "message_sent", vendor_id=vendor.id)
            any_success = True
        else:
            vendor.status = "failed"
            vendor.status_updated_at = datetime.utcnow()
            log_activity(db, event.id, f"Message to {vendor.name} failed: {result['error']}", "message_failed", vendor_id=vendor.id)

        results.append({"vendor_id": vendor.id, "ok": result["ok"], "wa_message_id": result.get("wa_message_id"), "error": result.get("error")})

    if any_success and event.status == "draft":
        event.status = "active"

    touch(db, event.id)
    db.commit()
    return {"results": results}
