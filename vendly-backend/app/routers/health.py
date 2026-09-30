"""E13 from Backend Spec section 5 / 10 ("Health response")."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services import payments_client

router = APIRouter(prefix="/api/v1", tags=["System"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as err:
        db_status = f"down: {err}"

    payments_status = "mock"
    try:
        payments_status = payments_client.get_mode()
    except Exception:
        payments_status = "down"

    whatsapp_configured = bool(settings.WHATSAPP_ACCESS_TOKEN and settings.WHATSAPP_PHONE_NUMBER_ID)

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "db": db_status,
        "payments": payments_status,
        "whatsapp_configured": whatsapp_configured,
        "mock_whatsapp_enabled": settings.USE_MOCK_WHATSAPP,
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION,
    }
