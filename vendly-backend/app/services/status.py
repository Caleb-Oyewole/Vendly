"""
Section 9 (Real-time updates): every write that changes something dashboard-
visible bumps events.version inside the same transaction, so the frontend's
short-poll (GET /events/{id}/status?since=N) can cheaply detect "nothing
changed" without re-sending the whole payload.
"""
from sqlalchemy.orm import Session

from app.models import Event


def touch(db: Session, event_id: int) -> int:
    """Increments events.version and returns the new value. Caller commits."""
    event = db.get(Event, event_id)
    if event is None:
        return 0
    event.version += 1
    db.add(event)
    db.flush()
    return event.version
