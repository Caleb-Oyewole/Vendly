"""Section 4.5: the activity feed shown on the dashboard."""
from sqlalchemy.orm import Session

from app.models import Activity

VALID_TYPES = {
    "event_created", "vendor_added", "message_sent", "message_failed",
    "message_delivered", "message_read", "vendor_confirmed", "vendor_declined",
    "payment_processing", "payment_paid", "payment_failed",
}


def log_activity(db: Session, event_id: int, text: str, type_: str, vendor_id: int | None = None) -> None:
    """Inserts one activity row. Caller commits as part of the larger transaction."""
    if type_ not in VALID_TYPES:
        # Fail loudly in dev rather than silently logging a typo'd type.
        raise ValueError(f"Unknown activity type: {type_}")
    db.add(Activity(event_id=event_id, vendor_id=vendor_id, type=type_, text=text))
