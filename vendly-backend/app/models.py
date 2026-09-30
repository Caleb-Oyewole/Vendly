"""
SQLAlchemy models matching Backend Spec section 4.1 exactly: events, vendors,
messages, payments, activity, webhook_events. Money columns are integers in
minor units (kobo). Timestamps are UTC.
"""
from datetime import datetime, date

from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, ForeignKey,
    CheckConstraint, UniqueConstraint, Index, func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    start_time = Column(String, nullable=False)  # 'HH:MM'
    venue = Column(String, nullable=False)
    notes = Column(Text, nullable=False, default="")
    currency = Column(String, nullable=False, default="NGN")
    status = Column(String, nullable=False, default="draft")
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendors = relationship("Vendor", back_populates="event", cascade="all, delete-orphan")
    activity = relationship("Activity", back_populates="event", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('draft','active','completed')", name="ck_event_status"),
    )


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)  # E.164 with '+'
    arrival_time = Column(String, nullable=False)  # 'HH:MM'
    deposit_amount = Column(Integer, nullable=False, default=0)  # kobo
    balance_amount = Column(Integer, nullable=False, default=0)  # kobo
    status = Column(String, nullable=False, default="pending")
    status_updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    event = relationship("Event", back_populates="vendors")
    messages = relationship("Message", back_populates="vendor", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="vendor", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','sent','confirmed','declined','failed')",
            name="ck_vendor_status",
        ),
        CheckConstraint("deposit_amount >= 0", name="ck_vendor_deposit_nonneg"),
        CheckConstraint("balance_amount >= 0", name="ck_vendor_balance_nonneg"),
        UniqueConstraint("event_id", "phone", name="uq_vendor_event_phone"),
        Index("ix_vendors_event", "event_id"),
        Index("ix_vendors_phone", "phone"),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    direction = Column(String, nullable=False)  # 'out' | 'in'
    wa_message_id = Column(String, unique=True, nullable=True)  # wamid.* from Meta
    kind = Column(String, nullable=False)  # template | interactive | button_reply | text
    payload = Column(Text, nullable=True)  # JSON string
    wa_status = Column(String, nullable=True)  # accepted|sent|delivered|read|failed
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="messages")

    __table_args__ = (
        CheckConstraint("direction IN ('out','in')", name="ck_message_direction"),
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    kind = Column(String, nullable=False)  # 'deposit' | 'balance'
    amount = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="NGN")
    status = Column(String, nullable=False, default="processing")
    provider = Column(String, nullable=False, default="mock")  # mock|paystack|flutterwave
    provider_ref = Column(String, nullable=True)
    idempotency_key = Column(String, nullable=False, unique=True)  # 'vendor:{id}:{kind}:{attempt}'
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="payments")

    __table_args__ = (
        CheckConstraint("kind IN ('deposit','balance')", name="ck_payment_kind"),
        CheckConstraint("status IN ('processing','paid','failed')", name="ck_payment_status"),
        # NOTE: SQLite/standard SQLAlchemy can't express the spec's partial
        # unique index (WHERE status IN (...)) portably. It's enforced in
        # code instead -- see routers/budget.py's "one live payment" check --
        # which is exercised by tests/test_budget.py.
    )


class Activity(Base):
    __tablename__ = "activity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True)
    type = Column(String, nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    event = relationship("Event", back_populates="activity")

    __table_args__ = (
        Index("ix_activity_event", "event_id", "id"),
    )


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wa_message_id = Column(String, unique=True, nullable=True)
    payload = Column(Text, nullable=False)
    processed = Column(Integer, nullable=False, default=0)
    received_at = Column(DateTime, nullable=False, default=datetime.utcnow)
