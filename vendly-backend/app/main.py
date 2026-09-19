from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session
import httpx

from app.database import Base, engine, get_db
from app import models, schemas, config

# Create tables in SQLite automatically
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

# --- Day 1 Core Endpoints ---

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

# --- Day 2 Endpoints: WhatsApp Integration ---

# GET Webhook: Handshakes with Meta Cloud API to verify endpoint ownership
@app.get("/api/v1/webhook/whatsapp")
def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == config.WHATSAPP_VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification token mismatch")

# POST Webhook: Receives button reply payload when vendor clicks Accept/Decline on WhatsApp
@app.post("/api/v1/webhook/whatsapp")
async def receive_whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    
    try:
        entries = data.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                for msg in messages:
                    if msg.get("type") == "interactive":
                        button_reply = msg.get("interactive", {}).get("button_reply", {})
                        button_id = button_reply.get("id")
                        
                        if button_id:
                            action, vendor_id_str = button_id.split("_")
                            vendor = db.query(models.Vendor).filter(models.Vendor.id == int(vendor_id_str)).first()
                            
                            if vendor:
                                vendor.status = "ACCEPTED" if action == "ACCEPTED" else "DECLINED"
                                db.commit()
    except Exception:
        pass  # Always return HTTP 200 to Meta even if payload structure is unexpected

    return {"status": "success"}

# POST Send Notification: Sends interactive button message to vendor via Meta Cloud API
@app.post("/api/v1/notify/send", response_model=schemas.NotificationResponse)
async def send_vendor_notification(payload: schemas.NotificationRequest):
    url = f"https://graph.facebook.com/v18.0/{config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    body = {
        "messaging_product": "whatsapp",
        "to": payload.phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": f"Hello {payload.vendor_name}, are you available for {payload.event_title}?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": f"ACCEPTED_{payload.vendor_id}", "title": "Accept"}
                    },
                    {
                        "type": "reply",
                        "reply": {"id": f"DECLINED_{payload.vendor_id}", "title": "Decline"}
                    }
                ]
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=body, headers=headers)
        
    if response.status_code not in [200, 201]:
        raise HTTPException(status_code=response.status_code, detail=response.text)
        
    res_data = response.json()
    message_id = res_data.get("messages", [{}])[0].get("id", "unknown")
    
    return {"status": "sent", "message_id": message_id}