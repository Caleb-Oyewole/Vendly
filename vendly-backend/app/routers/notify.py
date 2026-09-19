from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.whatsapp import WhatsAppClient, get_whatsapp_client

router = APIRouter(prefix="/api/v1/notify", tags=["Notification"])


class NotificationRequest(BaseModel):
    vendor_id: int
    phone_number: str
    vendor_name: str
    event_title: str


@router.post("/send")
def send_notification(
    payload: NotificationRequest,
    client: WhatsAppClient = Depends(get_whatsapp_client)
):
    """
    Sends an interactive message via the configured WhatsApp client interface.
    Switches seamlessly between Mock and Meta Cloud API based on USE_MOCK_WHATSAPP settings.
    """
    result = client.send_template(
        phone_number=payload.phone_number,
        vendor_name=payload.vendor_name,
        event_title=payload.event_title,
        vendor_id=payload.vendor_id
    )
    return {"message": "Notification dispatched successfully", "details": result}