from tests.conftest import make_event, confirm_via_webhook


def test_yes_reply_confirms_vendor(client):
    event = make_event(client)
    event_id, vendor_id = event["id"], event["vendors"][0]["id"]

    client.post("/api/v1/notify/send", json={"event_id": event_id})
    status_after_send = client.get(f"/api/v1/events/{event_id}").json()
    assert status_after_send["vendors"][0]["status"] == "sent"

    confirm_via_webhook(client, vendor_id, answer="YES")

    final = client.get(f"/api/v1/events/{event_id}").json()
    assert final["vendors"][0]["status"] == "confirmed"


def test_duplicate_webhook_delivery_is_ignored(client):
    """Same wa_message_id delivered twice must not double-process (spec 7.3.2)."""
    event = make_event(client)
    event_id, vendor_id = event["id"], event["vendors"][0]["id"]
    client.post("/api/v1/notify/send", json={"event_id": event_id})

    body = {
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"field": "messages", "value": {
            "messages": [{"from": "2348012345671", "id": "dup.msg.1",
                          "type": "button", "button": {"payload": f"YES:{vendor_id}", "text": "YES"}}],
        }}]}],
    }
    r1 = client.post("/api/v1/webhook/whatsapp", json=body)
    r2 = client.post("/api/v1/webhook/whatsapp", json=body)
    assert r1.status_code == 200 and r2.status_code == 200

    activity = client.get(f"/api/v1/events/{event_id}/status", params={"since": 0}).json()
    confirms = [a for a in activity["activity"] if a["type"] == "vendor_confirmed"]
    assert len(confirms) == 1
