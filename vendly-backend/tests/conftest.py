"""
Sets env vars BEFORE anything under app/ is imported, so tests run against a
throwaway SQLite file (never your real vendly.db), skip webhook signature
checking, and use the mock WhatsApp client. This must stay a plain module-
level block, not a fixture -- pytest imports conftest.py before it imports
the test files, so this is the only place guaranteed to run first.
"""
import os
import tempfile

_db_fd, _DB_PATH = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_DB_PATH}")
os.environ.setdefault("WEBHOOK_SKIP_SIGNATURE", "true")
os.environ.setdefault("USE_MOCK_WHATSAPP", "true")
os.environ.setdefault("PAYMENTS_FALLBACK_MOCK", "true")
os.environ.setdefault("PAYMENTS_BASE_URL", "http://127.0.0.1:9/unreachable")
os.environ.setdefault("DEMO_PHONES", "")

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


def make_event(client, deposit=5_000_000, balance=10_000_000, phone="+2348012345671"):
    body = {
        "name": "Test Event", "event_date": "2026-12-01", "start_time": "16:00",
        "venue": "Test Venue", "notes": "",
        "vendors": [{"role": "DJ", "name": "Test DJ", "phone": phone,
                     "arrival_time": "14:00", "deposit_amount": deposit, "balance_amount": balance}],
    }
    resp = client.post("/api/v1/events", json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


def confirm_via_webhook(client, vendor_id, answer="YES", phone="2348012345671"):
    body = {
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"field": "messages", "value": {
            "messages": [{"from": phone, "id": f"test.{vendor_id}.{answer}",
                          "type": "button", "button": {"payload": f"{answer}:{vendor_id}", "text": answer}}],
        }}]}],
    }
    resp = client.post("/api/v1/webhook/whatsapp", json=body)
    assert resp.status_code == 200, resp.text
