# app/routers/budget.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlite3 import Connection
from app.database import get_db
from app.schemas import EventBudgetResponse, VendorBudgetSummary

router = APIRouter(prefix="/api/v1/events", tags=["Budget"])


@router.get("/{event_id}/budget", response_model=EventBudgetResponse)
def get_event_budget(event_id: int, db: Connection = Depends(get_db)):
    """
    Calculates and returns the aggregated budget summary for a given event,
    including total costs, deposits paid, and remaining balances due.
    """
    cursor = db.cursor()

    # 1. Fetch event details safely using index positional tuples
    cursor.execute("SELECT id, title FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found",
        )

    # 2. Extract event attributes using integer indexing
    e_id = event[0]
    e_title = event[1]

    # 3. Fetch all vendors linked to this event
    cursor.execute(
        """
        SELECT id, name, role, status, deposit_amount, balance_amount 
        FROM vendors 
        WHERE event_id = ?
        """,
        (event_id,),
    )
    vendor_rows = cursor.fetchall()

    # 4. Aggregate financial totals safely
    vendor_summaries = []
    total_budget = 0.0
    total_deposits = 0.0
    total_balance = 0.0

    for row in vendor_rows:
        v_id, name, role, vendor_status, deposit, balance = row
        
        # Guard against None/NULL database values
        deposit_val = float(deposit) if deposit is not None else 0.0
        balance_val = float(balance) if balance is not None else 0.0
        v_total = deposit_val + balance_val

        total_deposits += deposit_val
        total_balance += balance_val
        total_budget += v_total

        vendor_summaries.append(
            VendorBudgetSummary(
                vendor_id=v_id,
                name=name,
                role=role or "Vendor",
                status=vendor_status or "PENDING",
                deposit_amount=deposit_val,
                balance_amount=balance_val,
                total_cost=v_total,
            )
        )

    # 5. Return aggregated response payload
    return EventBudgetResponse(
        event_id=e_id,
        event_title=e_title,
        total_budget=total_budget,
        total_deposits_paid=total_deposits,
        total_balance_due=total_balance,
        vendor_count=len(vendor_summaries),
        vendors=vendor_summaries,
    )