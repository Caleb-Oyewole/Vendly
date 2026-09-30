# app/routers/budget.py
"""
E11, E12 from Backend Spec sections 5, 5.1, 4.3. The previous budget.py only
summed raw vendor columns -- it had no Payment table, no disburse endpoint,
and none of the 409 rules that keep money-handling correct.
"""
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import NotFoundError, ConflictError, PaymentFailedError
from app.models import Event, Vendor, Payment
from app.schemas import DisburseRequest
from app.services import payments_client
from app.services.status import touch
from app.services.activity import log_activity

router = APIRouter(prefix="/api/v1", tags=["Budget"])


def _latest_payment(db: Session, vendor_id: int, kind: str) -> Payment | None:
    return (
        db.query(Payment)
        .filter(Payment.vendor_id == vendor_id, Payment.kind == kind)
        .order_by(Payment.id.desc()).first()
    )


@router.get("/events/{event_id}/budget")
def get_budget(event_id: int, db: Session = Depends(get_db)):
    """E11: totals and per-vendor deposit/balance state."""
    event = db.get(Event, event_id)
    if event is None:
        raise NotFoundError(f"Event {event_id} not found")

    vendors = db.query(Vendor).filter(Vendor.event_id == event_id).all()
    budget = sum(v.deposit_amount + v.balance_amount for v in vendors)
    deposits_paid = 0
    balances_paid = 0
    vendor_rows = []

    for v in vendors:
        deposit = _latest_payment(db, v.id, "deposit")
        balance = _latest_payment(db, v.id, "balance")
        if deposit and deposit.status == "paid":
            deposits_paid += deposit.amount
        if balance and balance.status == "paid":
            balances_paid += balance.amount

        vendor_rows.append({
            "vendor_id": v.id, "role": v.role, "name": v.name, "vendor_status": v.status,
            "deposit": {
                "amount": v.deposit_amount,
                "status": deposit.status if deposit else ("due" if v.status == "confirmed" else "not_due"),
                "paid_at": deposit.updated_at.isoformat() + "Z" if deposit and deposit.status == "paid" else None,
            },
            "balance": {
                "amount": v.balance_amount,
                "status": balance.status if balance else ("due" if deposit and deposit.status == "paid" else "not_due"),
                "paid_at": balance.updated_at.isoformat() + "Z" if balance and balance.status == "paid" else None,
            },
        })

    return {
        "event_id": event_id, "currency": event.currency, "mode": payments_client.get_mode(),
        "totals": {
            "budget": budget, "deposits_paid": deposits_paid, "balances_paid": balances_paid,
            "outstanding": budget - deposits_paid - balances_paid,
        },
        "vendors": vendor_rows,
    }


@router.post("/budget/{vendor_id}/disburse")
def disburse(vendor_id: int, payload: DisburseRequest, db: Session = Depends(get_db)):
    """E12. Rules enforced here, never in the client (spec 4.3):
      - deposit requires vendor.status == 'confirmed'
      - balance requires the deposit payment to already be 'paid'
      - at most one live (processing|paid) payment per vendor+kind
      - the amount always comes from the vendors row, never the request body
    """
    vendor = db.get(Vendor, vendor_id)
    if vendor is None:
        raise NotFoundError(f"Vendor {vendor_id} not found")

    kind = payload.kind

    if kind == "deposit" and vendor.status != "confirmed":
        raise ConflictError("Deposit requires the vendor to be confirmed first")

    if kind == "balance":
        deposit = _latest_payment(db, vendor_id, "deposit")
        if not deposit or deposit.status != "paid":
            raise ConflictError("Balance requires the deposit to be paid first")

    existing_live = (
        db.query(Payment)
        .filter(Payment.vendor_id == vendor_id, Payment.kind == kind, Payment.status.in_(["processing", "paid"]))
        .order_by(Payment.id.desc()).first()
    )
    if existing_live:
        return {"payment_id": existing_live.id, "kind": kind, "status": existing_live.status}

    attempt = db.query(Payment).filter(Payment.vendor_id == vendor_id, Payment.kind == kind).count() + 1
    idempotency_key = f"vendor:{vendor_id}:{kind}:{attempt}"
    amount = vendor.deposit_amount if kind == "deposit" else vendor.balance_amount

    payment = Payment(
        vendor_id=vendor_id, kind=kind, amount=amount, currency="NGN",
        status="processing", provider="mock", idempotency_key=idempotency_key,
    )
    db.add(payment)
    log_activity(db, vendor.event_id, f"{kind.capitalize()} payment started for {vendor.name}", "payment_processing", vendor_id=vendor_id)
    touch(db, vendor.event_id)
    db.commit()
    db.refresh(payment)

    result = payments_client.execute_payment(
        idempotency_key=idempotency_key, vendor_ref=str(vendor_id), amount=amount,
        currency="NGN", kind=kind, description=f"{kind.capitalize()}: {vendor.name}",
    )

    payment.provider = result.get("provider", "mock")
    payment.provider_ref = result.get("provider_ref")
    payment.status = result.get("status", "failed")
    payment.updated_at = datetime.utcnow()

    activity_type = "payment_paid" if payment.status == "paid" else "payment_failed"
    log_activity(db, vendor.event_id, f"{kind.capitalize()} for {vendor.name} {payment.status}", activity_type, vendor_id=vendor_id)
    touch(db, vendor.event_id)
    db.commit()

    return {"payment_id": payment.id, "kind": kind, "status": payment.status}
