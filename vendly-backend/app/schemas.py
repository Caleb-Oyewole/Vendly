# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional


# Day 1 Schemas
class EventCreate(BaseModel):
    title: str
    organizer_name: str


class VendorCreate(BaseModel):
    name: str
    role: str
    phone_number: str
    deposit_amount: float
    balance_amount: float


class VendorResponse(BaseModel):
    id: int
    event_id: int
    name: str
    role: str
    phone_number: str
    deposit_amount: float
    balance_amount: float
    status: str


class EventStatusResponse(BaseModel):
    event_id: int
    title: str
    organizer_name: str
    vendors: List[VendorResponse]


# Day 2 Schemas
class NotificationRequest(BaseModel):
    vendor_id: int
    phone_number: str
    vendor_name: str
    event_title: str


class NotificationResponse(BaseModel):
    message: str
    details: dict


# Day 3 Schemas
class VendorBudgetSummary(BaseModel):
    vendor_id: int
    name: str
    role: str
    status: str
    deposit_amount: float
    balance_amount: float
    total_cost: float


class EventBudgetResponse(BaseModel):
    event_id: int
    event_title: str
    total_budget: float
    total_deposits_paid: float
    total_balance_due: float
    vendor_count: int
    vendors: List[VendorBudgetSummary]