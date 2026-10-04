"""
SQLAlchemy models matching Backend Spec section 4.1 exactly: events, vendors,
messages, payments, activity, webhook_events. Money columns are integers in
minor units (kobo). Timestamps are UTC.

Uses SQLAlchemy 2.0's typed declarative style (Mapped[...] / mapped_column())
rather than the older Column(...) style, so Pylance/mypy see the real Python
type on every attribute (str, int, datetime) instead of a bare Column[...]
descriptor. Purely a type-checking improvement -- the runtime behavior and
database schema are identical either way.
"""
from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    String, Text, Date, DateTime, ForeignKey,
    CheckConstraint, UniqueConstraint, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[str] = mapped_column(String, nullable=False)  # 'HH:MM'
    venue: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    currency: Mapped[str] = mapped_column(String, nullable=False, default="NGN")
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")
    version: Mapped[int] = mapped_column(nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendors: Mapped[list["Vendor"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    activity: Mapped[list["Activity"]] = relationship(back_populates="event", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('draft','active','completed')", name="ck_event_status"),
    )


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)  # E.164 with '+'
    arrival_time: Mapped[str] = mapped_column(String, nullable=False)  # 'HH:MM'
    deposit_amount: Mapped[int] = mapped_column(nullable=False, default=0)  # kobo
    balance_amount: Mapped[int] = mapped_column(nullable=False, default=0)  # kobo
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    status_updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    event: Mapped["Event"] = relationship(back_populates="vendors")
    messages: Mapped[list["Message"]] = relationship(back_populates="vendor", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship(back_populates="vendor", cascade="all, delete-orphan")

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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    direction: Mapped[str] = mapped_column(String, nullable=False)  # 'out' | 'in'
    wa_message_id: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)  # wamid.* from Meta
    kind: Mapped[str] = mapped_column(String, nullable=False)  # template | interactive | button_reply | text
    payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    wa_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # accepted|sent|delivered|read|failed
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    vendor: Mapped["Vendor"] = relationship(back_populates="messages")

    __table_args__ = (
        CheckConstraint("direction IN ('out','in')", name="ck_message_direction"),
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False)  # 'deposit' | 'balance'
    amount: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="NGN")
    status: Mapped[str] = mapped_column(String, nullable=False, default="processing")
    provider: Mapped[str] = mapped_column(String, nullable=False, default="mock")  # mock|paystack|flutterwave
    provider_ref: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)  # 'vendor:{id}:{kind}:{attempt}'
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendor: Mapped["Vendor"] = relationship(back_populates="payments")

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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    vendor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    event: Mapped["Event"] = relationship(back_populates="activity")

    __table_args__ = (
        Index("ix_activity_event", "event_id", "id"),
    )


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    wa_message_id: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    processed: Mapped[int] = mapped_column(nullable=False, default=0)
    received_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)