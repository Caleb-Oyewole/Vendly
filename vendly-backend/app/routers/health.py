# app/routers/health.py
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlite3 import Connection
from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/api/v1", tags=["System"])


@router.get("/health")
def health_check(db: Connection = Depends(get_db)):
    """
    System Health Check Endpoint.
    Verifies API readiness and tests database connectivity.
    """
    try:
        # Test database read capability
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        db_status = "connected"
    except Exception as err:
        db_status = f"unhealthy: {str(err)}"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": db_status,
                "environment": settings.APP_ENV,
            },
        )

    return {
        "status": "healthy",
        "database": db_status,
        "environment": settings.APP_ENV,
        "mock_whatsapp_enabled": settings.USE_MOCK_WHATSAPP,
    }