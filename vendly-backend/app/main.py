from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import Base, engine, get_db
from app import models, schemas

# Automatically create all database tables in SQLite on app start
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vendly API", version="1.0.0")

@app.get("/")
def root():
    return {
        "message": "Welcome to Vendly API!",
        "docs": "Visit /docs for the interactive API documentation"
    }
    
@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/events", response_model=schemas.EventStatusResponse, status_code=status.HTTP_201_CREATED)
def create_event(event_data: schemas.EventCreate, db: Session = Depends(get_db)):
    db_event = models.Event(
        title=event_data.title,
        organizer_name=event_data.organizer_name
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.post("/api/v1/events/{id}/vendors", response_model=schemas.VendorResponse, status_code=status.HTTP_201_CREATED)
def add_vendor_to_event(id: int, vendor_data: schemas.VendorCreate, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db_vendor = models.Vendor(
        event_id=id,
        name=vendor_data.name,
        role=vendor_data.role,
        phone_number=vendor_data.phone_number,
        deposit_amount=vendor_data.deposit_amount,
        balance_amount=vendor_data.balance_amount
    )
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

@app.get("/api/v1/events/{id}/status", response_model=schemas.EventStatusResponse)
def get_event_status(id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event