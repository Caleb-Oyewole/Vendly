"""E4, E5, E6 from Backend Spec section 5. E5/E6 did not exist before this."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import NotFoundError, ConflictError
from app.models import Event, Vendor, Payment
from app.schemas import VendorCreate, VendorPatch
from app.services.status import touch
from app.services.activity import log_activity
from app.routers.events import serialize_vendor_full

router = APIRouter(prefix="/api/v1/events/{event_id}/vendors", tags=["Vendors"])


def _get_event_or_404(db: Session, event_id: int) -> Event:
    event = db.get(Event, event_id)
    if event is None:
        raise NotFoundError(f"Event {event_id} not found")
    return event


@router.post("", status_code=status.HTTP_201_CREATED)
def add_vendors(event_id: int, payload: list[VendorCreate], db: Session = Depends(get_db)):
    """E4: add one or many vendors. 409 on (event_id, phone) duplicate."""
    _get_event_or_404(db, event_id)
    created = []
    for v in payload:
        existing = db.query(Vendor).filter(Vendor.event_id == event_id, Vendor.phone == v.phone).first()
        if existing:
            raise ConflictError(f"A vendor with phone {v.phone} already exists on this event")
        vendor = Vendor(
            event_id=event_id, role=v.role, name=v.name, phone=v.phone,
            arrival_time=v.arrival_time, deposit_amount=v.deposit_amount,
            balance_amount=v.balance_amount, status="pending",
        )
        db.add(vendor)
        db.flush()
        log_activity(db, event_id, f"{v.name} ({v.role}) added", "vendor_added", vendor_id=vendor.id)
        created.append(vendor)

    touch(db, event_id)
    db.commit()
    return [serialize_vendor_full(db, v) for v in created]


@router.patch("/{vendor_id}")
def edit_vendor(event_id: int, vendor_id: int, payload: VendorPatch, db: Session = Depends(get_db)):
    """E5: edit vendor fields. 409 if a payment already exists for this vendor,
    since amounts must not change after money has moved (spec 4.3)."""
    _get_event_or_404(db, event_id)
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id, Vendor.event_id == event_id).first()
    if vendor is None:
        raise NotFoundError(f"Vendor {vendor_id} not found on event {event_id}")

    has_payment = db.query(Payment).filter(Payment.vendor_id == vendor_id).first() is not None
    changing_amounts = payload.deposit_amount is not None or payload.balance_amount is not None
    if has_payment and changing_amounts:
        raise ConflictError("Cannot change amounts after a payment exists for this vendor")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vendor, field, value)

    touch(db, event_id)
    db.commit()
    return serialize_vendor_full(db, vendor)


@router.delete("/{vendor_id}", status_code=status.HTTP_200_OK)
def delete_vendor(event_id: int, vendor_id: int, db: Session = Depends(get_db)):
    """E6: remove a vendor. 409 if a payment exists for them."""
    _get_event_or_404(db, event_id)
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id, Vendor.event_id == event_id).first()
    if vendor is None:
        raise NotFoundError(f"Vendor {vendor_id} not found on event {event_id}")

    if db.query(Payment).filter(Payment.vendor_id == vendor_id).first() is not None:
        raise ConflictError("Cannot delete a vendor with an existing payment")

    db.delete(vendor)
    touch(db, event_id)
    db.commit()
    return {"deleted": True, "id": vendor_id}
