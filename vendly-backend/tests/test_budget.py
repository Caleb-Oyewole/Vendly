from tests.conftest import make_event, confirm_via_webhook


def test_deposit_requires_confirmed_vendor(client):
    event = make_event(client)
    vendor_id = event["vendors"][0]["id"]
    resp = client.post(f"/api/v1/budget/{vendor_id}/disburse", json={"kind": "deposit"})
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "CONFLICT"


def test_balance_requires_paid_deposit(client):
    event = make_event(client)
    vendor_id = event["vendors"][0]["id"]
    client.post("/api/v1/notify/send", json={"event_id": event["id"]})
    confirm_via_webhook(client, vendor_id)

    resp = client.post(f"/api/v1/budget/{vendor_id}/disburse", json={"kind": "balance"})
    assert resp.status_code == 409


def test_deposit_pays_via_mock_fallback_when_php_service_unreachable(client):
    event = make_event(client)
    vendor_id = event["vendors"][0]["id"]
    client.post("/api/v1/notify/send", json={"event_id": event["id"]})
    confirm_via_webhook(client, vendor_id)

    resp = client.post(f"/api/v1/budget/{vendor_id}/disburse", json={"kind": "deposit"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "paid"  # PAYMENTS_FALLBACK_MOCK=true in conftest

    repeat = client.post(f"/api/v1/budget/{vendor_id}/disburse", json={"kind": "deposit"})
    assert repeat.json()["payment_id"] == body["payment_id"]  # one live payment per vendor+kind
