# app/main.py
from fastapi import FastAPI, Request, Response, HTTPException, status
from app.config import settings

# Import all modular routers
from app.routers import budget, events, notify

app = FastAPI(
    title="Vendly API",
    version="1.0.0",
    description="Backend service for event vendor management and WhatsApp automated notifications"
)

# Include all APIRouters to expose endpoints and schemas in Swagger UI
app.include_router(events.router)
app.include_router(notify.router)
app.include_router(budget.router)


@app.get("/", tags=["Default"])
def read_root():
    """Root status check route."""
    return {"message": "Vendly API is active"}


@app.get("/api/v1/health", tags=["Default"])
def health_check():
    """System health check endpoint for monitoring API status."""
    return {"status": "healthy", "environment": settings.APP_ENV}


@app.get("/api/v1/webhook/whatsapp", tags=["Default"])
def verify_webhook(request: Request):
    """Meta Webhook Challenge Verification Route."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification token mismatch",
    )


@app.post("/api/v1/webhook/whatsapp", tags=["Default"])
async def receive_webhook(payload: dict):
    """Receives button response webhooks from WhatsApp/Mock client."""
    try:
        entries = payload.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    if msg.get("type") == "interactive":
                        button_reply = msg.get("interactive", {}).get("button_reply", {})
                        reply_id = button_reply.get("id", "")
                        print(f"Received interactive button response: {reply_id}")
        return {"status": "success"}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )