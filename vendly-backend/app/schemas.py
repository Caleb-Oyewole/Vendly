from typing import List
from pydantic import BaseModel, ConfigDict

# Base schema for Vendor creation request
class VendorCreate(BaseModel):
    name: str
    role: str
    phone_number: str
    deposit_amount: float
    balance_amount: float

# Response schema for returning Vendor details
class VendorResponse(VendorCreate):
    id: int
    event_id: int
    status: str

    model_config = ConfigDict(from_attributes=True)

# Base schema for Event creation request
class EventCreate(BaseModel):
    title: str
    organizer_name: str

# Response schema for returning full Event status
class EventStatusResponse(BaseModel):
    id: int
    title: str
    organizer_name: str
    vendors: List[VendorResponse] = []

    model_config = ConfigDict(from_attributes=True)
    
class NotificationRequest(BaseModel):
    vendor_id: int
    phone_number: str
    vendor_name: str
    event_title: str

class NotificationResponse(BaseModel):
    status: str
    message_id: str