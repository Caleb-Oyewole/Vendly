"""E1, E2, E3, E7 from Backend Spec section 5."""
from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.errors import NotFoundError
from app.models import Event, Vendor, Payment, Activity
from app.schemas import EventCreate
from app.services.activity import log_activity

router = APIRouter(prefix="/api/v1/events", tags=["Events"])


def _vendor_money_status(db: Session, vendor: Vendor) -> dict:
    """Derives deposit/balance display status per spec 4.3 / 4.4."""
    deposit_payment = (
        db.query(Payment)
        .filter(Payment.vendor_id == vendor.id, Payment.kind == "deposit")
        .order_by(Payment.id.desc()).first()
    )
    balance_payment = (
        db.query(Payment)
        .filter(Payment.vendor_id == vendor.id, Payment.kind == "balance")
        .order_by(Payment.id.desc()).first()
    )

    def status_for(payment: Payment | None, prerequisite_met: bool) -> str:
        if payment and payment.status in ("processing", "paid"):
            return payment.status
        return "due" if prerequisite_met else "not_due"

    deposit_status = status_for(deposit_payment, vendor.status == "confirmed")
    balance_status = status_for(balance_payment, deposit_payment is not None and deposit_payment.status == "paid")

    return {
        "deposit": {"amount": vendor.deposit_amount, "status": deposit_status},
        "balance": {"amount": vendor.balance_amount, "status": balance_status},
    }


def serialize_vendor_full(db: Session, vendor: Vendor) -> dict:
    money = _vendor_money_status(db, vendor)
    return {
        "id": vendor.id, "role": vendor.role, "name": vendor.name, "phone": vendor.phone,
        "arrival_time": vendor.arrival_time, "status": vendor.status,
        "status_updated_at": vendor.status_updated_at.isoformat() + "Z",
        **money,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    """E1: create an event with its vendors in one call."""
    event = Event(
        name=payload.name, event_date=payload.event_date, start_time=payload.start_time,
        venue=payload.venue, notes=payload.notes, status="draft", version=1,
    )
    db.add(event)
    db.flush()  # get event.id before inserting vendors

    for v in payload.vendors:
        db.add(Vendor(
            event_id=event.id, role=v.role, name=v.name, phone=v.phone,
            arrival_time=v.arrival_time, deposit_amount=v.deposit_amount,
            balance_amount=v.balance_amount, status="pending",
        ))

    log_activity(db, event.id, f"Event '{event.name}' created", "event_created")
    for v in payload.vendors:
        log_activity(db, event.id, f"{v.name} ({v.role}) added", "vendor_added")

    db.commit()
    db.refresh(event)

    vendors = db.query(Vendor).filter(Vendor.event_id == event.id).all()
    return {
        "id": event.id, "name": event.name, "status": event.status, "version": event.version,
        "vendors": [serialize_vendor_full(db, v) for v in vendors],
    }


@router.get("")
def list_events(db: Session = Depends(get_db)):
    """E2: events with vendor_count, confirmed_count, total_budget."""
    events = db.query(Event).order_by(Event.created_at.desc()).all()
    out = []
    for e in events:
        vendors = db.query(Vendor).filter(Vendor.event_id == e.id).all()
        confirmed = sum(1 for v in vendors if v.status == "confirmed")
        budget = sum(v.deposit_amount + v.balance_amount for v in vendors)
        out.append({
            "id": e.id, "name": e.name, "event_date": e.event_date.isoformat(),
            "venue": e.venue, "status": e.status, "vendor_count": len(vendors),
            "confirmed_count": confirmed, "total_budget": budget,
        })
    return out


@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    """E3: event with vendors, for the edit page / a deep link (no polling)."""
    event = db.get(Event, event_id)
    if event is None:
        raise NotFoundError(f"Event {event_id} not found")
    vendors = db.query(Vendor).filter(Vendor.event_id == event_id).all()
    return {
        "id": event.id, "name": event.name, "event_date": event.event_date.isoformat(),
        "start_time": event.start_time, "venue": event.venue, "notes": event.notes,
        "status": event.status, "version": event.version,
        "vendors": [serialize_vendor_full(db, v) for v in vendors],
    }


@router.get("/{event_id}/status")
def get_event_status(event_id: int, since: int = 0, db: Session = Depends(get_db)):
    """E7: cheap poll. Returns {"changed": false, "version": N} if nothing
    changed since `since`, else the full status payload."""
    event = db.get(Event, event_id)
    if event is None:
        raise NotFoundError(f"Event {event_id} not found")

    if since == event.version:
        return {"changed": False, "version": event.version}

    vendors = db.query(Vendor).filter(Vendor.event_id == event_id).all()
    summary = {
        "total": len(vendors),
        "confirmed": sum(1 for v in vendors if v.status == "confirmed"),
        "sent": sum(1 for v in vendors if v.status == "sent"),
        "declined": sum(1 for v in vendors if v.status == "declined"),
        "pending": sum(1 for v in vendors if v.status == "pending"),
        "failed": sum(1 for v in vendors if v.status == "failed"),
    }
    activity_rows = (
        db.query(Activity).filter(Activity.event_id == event_id)
        .order_by(Activity.id.desc()).limit(20).all()
    )
    return {
        "changed": True, "version": event.version,
        "event": {
            "id": event.id, "name": event.name, "event_date": event.event_date.isoformat(),
            "start_time": event.start_time, "venue": event.venue, "status": event.status,
        },
        "summary": summary,
        "vendors": [serialize_vendor_full(db, v) for v in vendors],
        "activity": [
            {"id": a.id, "type": a.type, "vendor_id": a.vendor_id, "text": a.text,
             "created_at": a.created_at.isoformat() + "Z"}
            for a in activity_rows
        ],
    }
