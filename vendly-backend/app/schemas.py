"""
Pydantic v2 schemas matching Backend Spec section 5 (API contract) exactly.
Amounts are integers in minor units (kobo). Phones are E.164 with '+'.
"""
import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator

PHONE_RE = re.compile(r"^\+[1-9]\d{7,14}$")
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class VendorCreate(BaseModel):
    role: str
    name: str
    phone: str
    arrival_time: str
    deposit_amount: int = 0
    balance_amount: int = 0

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not PHONE_RE.match(v):
            raise ValueError("Use international format, e.g. +2348012345671")
        return v

    @field_validator("arrival_time")
    @classmethod
    def validate_time(cls, v: str) -> str:
        if not TIME_RE.match(v):
            raise ValueError("Use 24h HH:MM format, e.g. 14:00")
        return v

    @field_validator("deposit_amount", "balance_amount")
    @classmethod
    def validate_nonneg(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Amount must be zero or positive")
        return v


class VendorPatch(BaseModel):
    role: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    arrival_time: Optional[str] = None
    deposit_amount: Optional[int] = None
    balance_amount: Optional[int] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None and not PHONE_RE.match(v):
            raise ValueError("Use international format, e.g. +2348012345671")
        return v


class EventCreate(BaseModel):
    name: str
    event_date: date
    start_time: str
    venue: str
    notes: str = ""
    vendors: list[VendorCreate] = []

    @field_validator("start_time")
    @classmethod
    def validate_time(cls, v: str) -> str:
        if not TIME_RE.match(v):
            raise ValueError("Use 24h HH:MM format, e.g. 16:00")
        return v


class NotifySendRequest(BaseModel):
    event_id: int
    vendor_ids: Optional[list[int]] = None  # omit = all pending/failed vendors


class DisburseRequest(BaseModel):
    kind: str  # "deposit" | "balance"

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, v: str) -> str:
        if v not in ("deposit", "balance"):
            raise ValueError("kind must be 'deposit' or 'balance'")
        return v
