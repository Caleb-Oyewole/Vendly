from fastapi import FastAPI, Request, Response, HTTPException, status
import httpx
from app.config import settings
from app.services.whatsapp import get_whatsapp_client

app = FastAPI(title="Vendly API")


@app.get("/")
def read_root():
    return {"message": "Vendly API is active"}


@app.get("/api/v1/webhook/whatsapp")
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


@app.post("/api/v1/webhook/whatsapp")
async def receive_webhook(payload: dict):
    """Receives button response webhooks from WhatsApp/Mock and updates state."""
    try:
        entries = payload.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    if msg.get("type") == "interactive":
                        button_reply = msg.get("interactive", {}).get(
                            "button_reply", {}
                        )
                        reply_id = button_reply.get("id", "")
                        print(f"Received interactive button response: {reply_id}")
        return {"status": "success"}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )