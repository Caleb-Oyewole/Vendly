# app/routers/events.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlite3 import Connection
from app.database import get_db
from app.schemas import EventCreate, EventStatusResponse, VendorCreate, VendorResponse

router = APIRouter(prefix="/api/v1/events", tags=["Events"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Connection = Depends(get_db)):
    """Creates a new event."""
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO events (title, organizer_name) VALUES (?, ?)",
        (payload.title, payload.organizer_name),
    )
    db.commit()
    event_id = cursor.lastrowid
    return {"id": event_id, "title": payload.title, "organizer_name": payload.organizer_name}


@router.post("/{event_id}/vendors", status_code=status.HTTP_201_CREATED)
def add_vendor_to_event(
    event_id: int, payload: VendorCreate, db: Connection = Depends(get_db)
):
    """Adds a vendor to an existing event."""
    cursor = db.cursor()
    cursor.execute("SELECT id FROM events WHERE id = ?", (event_id,))
    if not cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found",
        )

    cursor.execute(
        """
        INSERT INTO vendors (event_id, name, role, phone_number, deposit_amount, balance_amount, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            payload.name,
            payload.role,
            payload.phone_number,
            payload.deposit_amount,
            payload.balance_amount,
            "PENDING",
        ),
    )
    db.commit()
    vendor_id = cursor.lastrowid
    return {"id": vendor_id, "event_id": event_id, "status": "PENDING"}


@router.get("/{event_id}/status", response_model=EventStatusResponse)
def get_event_status(event_id: int, db: Connection = Depends(get_db)):
    """Retrieves full event status along with all associated vendors."""
    cursor = db.cursor()
    cursor.execute("SELECT id, title, organizer_name FROM events WHERE id = ?", (event_id,))
    event_row = cursor.fetchone()

    if not event_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found",
        )

    cursor.execute(
        """
        SELECT id, event_id, name, role, phone_number, deposit_amount, balance_amount, status
        FROM vendors WHERE event_id = ?
        """,
        (event_id,),
    )
    vendor_rows = cursor.fetchall()

    vendors = [
        VendorResponse(
            id=row[0],
            event_id=row[1],
            name=row[2],
            role=row[3],
            phone_number=row[4],
            deposit_amount=row[5],
            balance_amount=row[6],
            status=row[7],
        )
        for row in vendor_rows
    ]

    return EventStatusResponse(
        event_id=event_row["id"],
        title=event_row["title"],
        organizer_name=event_row["organizer_name"],
        vendors=vendors,
    )