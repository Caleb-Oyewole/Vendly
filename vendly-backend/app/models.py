from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    organizer_name = Column(String, nullable=False)

    # One event can have multiple vendors attached to it
    vendors = relationship("Vendor", back_populates="event", cascade="all, delete-orphan")


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    status = Column(String, default="PENDING")  # Statuses: PENDING, ACCEPTED, DECLINED
    deposit_amount = Column(Float, default=0.0)
    balance_amount = Column(Float, default=0.0)

    event = relationship("Event", back_populates="vendors")