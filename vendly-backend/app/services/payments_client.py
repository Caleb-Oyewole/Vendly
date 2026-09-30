"""
Section 8: the core talks to the PHP payments service over REST with an
X-Internal-Key shared secret. It has an 8s timeout and, if unreachable and
PAYMENTS_FALLBACK_MOCK=true, the core itself marks the payment paid with
provider "mock" so the demo never stalls on a flaky sandbox integration.
"""
import logging

import requests

from app.config import settings

logger = logging.getLogger("uvicorn")


def execute_payment(idempotency_key: str, vendor_ref: str, amount: int, currency: str, kind: str, description: str) -> dict:
    """Returns {"provider": str, "provider_ref": str, "status": "paid"|"processing"|"failed", "message": str}."""
    url = f"{settings.PAYMENTS_BASE_URL}/internal/payments"
    headers = {"X-Internal-Key": settings.PAYMENTS_SHARED_SECRET, "Content-Type": "application/json"}
    body = {
        "idempotency_key": idempotency_key, "vendor_ref": vendor_ref, "amount": amount,
        "currency": currency, "kind": kind, "description": description,
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=8)
        if resp.status_code >= 400:
            return {"provider": "mock", "provider_ref": None, "status": "failed", "message": f"payments service returned {resp.status_code}"}
        return resp.json()
    except requests.RequestException as exc:
        logger.warning(f"[PAYMENTS] Service unreachable: {exc}")
        if settings.PAYMENTS_FALLBACK_MOCK:
            return {"provider": "mock", "provider_ref": f"fallback_{idempotency_key}", "status": "paid", "message": "payments service unreachable; fell back to mock"}
        return {"provider": "mock", "provider_ref": None, "status": "failed", "message": str(exc)}


def get_mode() -> str:
    """Used by E11 to report whether the budget tab is running against
    mock or sandbox money, by asking the PHP service what mode it's in."""
    try:
        resp = requests.get(f"{settings.PAYMENTS_BASE_URL}/internal/health", timeout=3)
        if resp.status_code == 200:
            return resp.json().get("mode", "mock")
    except requests.RequestException:
        pass
    return "mock"
