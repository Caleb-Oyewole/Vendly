"""
Section 4.6. Runs automatically on startup when the events table is empty,
so a Render restart (or a teammate's first `uvicorn` run) never leaves an
empty demo. Reproduces the exact numbers used in the wireframes: deposits
total NGN 350,000, balances NGN 625,000, budget NGN 975,000.
"""
from datetime import date

from app.config import settings
from app.database import SessionLocal
from app.models import Event, Vendor, Activity

# Amounts in kobo (minor units). Falls back to obviously-fake numbers if
# DEMO_PHONES isn't set -- set it before your first real WhatsApp test.
FALLBACK_PHONES = ["+2348010000001", "+2348010000002", "+2348010000003", "+2348010000004", "+2348010000005"]

VENDOR_PLAN = [
    # role,          name,             deposit (kobo), balance (kobo)
    ("DJ",           "Kola Beats",      5_000_000, 10_000_000),
    ("Caterer",      "Amara's Kitchen", 15_000_000, 25_000_000),
    ("Photographer", "Tunde Lens",      5_000_000, 10_000_000),
    ("Decorator",    "Bloom Decor",     7_500_000, 12_500_000),
    ("MC",           "Emcee Femi",      2_500_000, 5_000_000),
]


def run_if_empty() -> None:
    db = SessionLocal()
    try:
        if db.query(Event).first() is not None:
            return  # already seeded

        phones = settings.demo_phone_list or FALLBACK_PHONES
        event = Event(
            name="Amara's 30th Birthday Gala",
            event_date=date(2026, 11, 14),
            start_time="16:00",
            venue="Eko Hotel, Lagos",
            notes="Demo seed data",
            status="draft",
            version=1,
        )
        db.add(event)
        db.flush()

        for i, (role, name, deposit, balance) in enumerate(VENDOR_PLAN):
            phone = phones[i] if i < len(phones) else FALLBACK_PHONES[i]
            db.add(Vendor(
                event_id=event.id, role=role, name=name, phone=phone,
                arrival_time="14:00", deposit_amount=deposit, balance_amount=balance,
                status="pending",
            ))

        db.add(Activity(event_id=event.id, type="event_created", text=f"Event '{event.name}' created (seed data)"))
        db.commit()
    finally:
        db.close()
