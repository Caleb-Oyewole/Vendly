from tests.conftest import make_event


def test_create_list_and_get_event(client):
    event = make_event(client)
    event_id = event["id"]
    assert event["status"] == "draft"
    assert event["version"] == 1
    assert len(event["vendors"]) == 1

    listed = client.get("/api/v1/events").json()
    assert any(e["id"] == event_id for e in listed)

    fetched = client.get(f"/api/v1/events/{event_id}").json()
    assert fetched["name"] == "Test Event"


def test_status_poll_reports_unchanged_then_changed(client):
    event = make_event(client)
    event_id, version = event["id"], event["version"]

    unchanged = client.get(f"/api/v1/events/{event_id}/status", params={"since": version}).json()
    assert unchanged == {"changed": False, "version": version}

    vendor_id = event["vendors"][0]["id"]
    patch_resp = client.patch(f"/api/v1/events/{event_id}/vendors/{vendor_id}", json={"name": "Renamed DJ"})
    assert patch_resp.status_code == 200

    changed = client.get(f"/api/v1/events/{event_id}/status", params={"since": version}).json()
    assert changed["changed"] is True
    assert changed["version"] == version + 1
    assert changed["vendors"][0]["name"] == "Renamed DJ"
