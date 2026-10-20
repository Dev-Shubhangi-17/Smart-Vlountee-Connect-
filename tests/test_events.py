"""Tests for event listing, searching, filtering, and CRUD operations."""

from datetime import date, timedelta


def test_list_events_and_filters(client, db_session, sample_event):
    """Test listing events with search and filters."""
    # List all
    res = client.get("/api/events")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total"] >= 1
    assert data["events"][0]["title"] == sample_event.title

    # Filter by city
    res_city = client.get("/api/events?city=Mumbai")
    assert res_city.status_code == 200
    assert len(res_city.get_json()["events"]) >= 1

    res_wrong_city = client.get("/api/events?city=NonExistentCity")
    assert res_wrong_city.status_code == 200
    assert len(res_wrong_city.get_json()["events"]) == 0

    # Filter by category
    res_cat = client.get("/api/events?category=Environment")
    assert res_cat.status_code == 200
    assert len(res_cat.get_json()["events"]) >= 1

    # Search keyword
    res_search = client.get("/api/events?search=Plantation")
    assert res_search.status_code == 200
    assert len(res_search.get_json()["events"]) >= 1


def test_get_event_detail(client, db_session, sample_event):
    """Test retrieving a single event by ID."""
    res = client.get(f"/api/events/{sample_event.id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == sample_event.id
    assert data["ngo"]["name"] == "Test NGO Foundation"


def test_get_event_not_found(client, db_session):
    """Test retrieving non-existent event returns 404."""
    res = client.get("/api/events/99999")
    assert res.status_code == 404


def test_ngo_create_event_success(client, db_session, ngo_headers):
    """Test NGO creating a new event."""
    payload = {
        "title": "Beach Cleanup Drive",
        "description": "Cleaning plastic waste from the coast",
        "category": "Environment",
        "city": "Mumbai",
        "venue": "Juhu Beach, Mumbai",
        "event_date": (date.today() + timedelta(days=10)).isoformat(),
        "start_time": "06:30",
        "duration_hours": 3.5,
        "max_volunteers": 40
    }
    res = client.post("/api/events", json=payload, headers=ngo_headers)
    assert res.status_code == 201
    data = res.get_json()
    assert data["event"]["title"] == "Beach Cleanup Drive"
    assert data["event"]["duration_hours"] == 3.5


def test_volunteer_forbidden_from_creating_event(client, db_session, volunteer_headers):
    """Test volunteer cannot create an event (403 forbidden)."""
    payload = {
        "title": "Unauthorized Event",
        "event_date": (date.today() + timedelta(days=5)).isoformat()
    }
    res = client.post("/api/events", json=payload, headers=volunteer_headers)
    assert res.status_code == 403
    assert "Only NGOs" in res.get_json()["error"]


def test_ngo_update_and_cancel_event(client, db_session, ngo_headers, sample_event):
    """Test NGO updating and cancelling their own event."""
    # Update
    update_res = client.put(f"/api/events/{sample_event.id}", json={
        "venue": "Updated Venue Location",
        "max_volunteers": 35
    }, headers=ngo_headers)
    assert update_res.status_code == 200
    assert update_res.get_json()["event"]["venue"] == "Updated Venue Location"
    assert update_res.get_json()["event"]["max_volunteers"] == 35

    # Cancel (soft delete)
    cancel_res = client.delete(f"/api/events/{sample_event.id}", headers=ngo_headers)
    assert cancel_res.status_code == 200
    assert "cancelled successfully" in cancel_res.get_json()["message"]
