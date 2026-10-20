"""Tests for event enrollment, duplicate prevention, capacity enforcement, and unenrollment."""

from datetime import date, timedelta
from app.models.event import Event


def test_volunteer_enrollment_success(client, db_session, volunteer_headers, sample_event):
    """Test successful volunteer enrollment."""
    res = client.post(f"/api/events/{sample_event.id}/enroll", headers=volunteer_headers)
    assert res.status_code == 201
    data = res.get_json()
    assert "Successfully enrolled" in data["message"]
    assert data["enrollment"]["event_id"] == sample_event.id


def test_duplicate_enrollment_prevention(client, db_session, volunteer_headers, sample_event):
    """Test volunteer cannot enroll twice in the same event."""
    client.post(f"/api/events/{sample_event.id}/enroll", headers=volunteer_headers)
    res_dup = client.post(f"/api/events/{sample_event.id}/enroll", headers=volunteer_headers)
    assert res_dup.status_code == 409
    assert "already enrolled" in res_dup.get_json()["error"]


def test_enrollment_capacity_full_prevention(client, db_session, volunteer_headers, sample_ngo):
    """Test enrolling in a full event returns 400."""
    # Create event with capacity 1
    event = Event(
        ngo_id=sample_ngo.id,
        title="Exclusive Workshop",
        event_date=date.today() + timedelta(days=5),
        max_volunteers=1,
        status="active"
    )
    db_session.add(event)
    db_session.commit()

    # First volunteer enrolls
    client.post(f"/api/events/{event.id}/enroll", headers=volunteer_headers)

    # Register second volunteer
    reg_res = client.post("/api/auth/volunteer/register", json={
        "name": "Second Volunteer",
        "email": "second@test.com",
        "password": "password123"
    })
    token2 = reg_res.get_json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}", "Content-Type": "application/json"}

    # Attempt second enrollment
    res_full = client.post(f"/api/events/{event.id}/enroll", headers=headers2)
    assert res_full.status_code == 400
    assert "full" in res_full.get_json()["error"]


def test_volunteer_unenroll_success(client, db_session, volunteer_headers, sample_event):
    """Test volunteer can unenroll from an upcoming event."""
    client.post(f"/api/events/{sample_event.id}/enroll", headers=volunteer_headers)
    res = client.delete(f"/api/events/{sample_event.id}/enroll", headers=volunteer_headers)
    assert res.status_code == 200
    assert "Successfully un-enrolled" in res.get_json()["message"]


def test_ngo_view_event_enrollments(client, db_session, ngo_headers, volunteer_headers, sample_event):
    """Test NGO can view all volunteers enrolled in their event."""
    client.post(f"/api/events/{sample_event.id}/enroll", headers=volunteer_headers)

    res = client.get(f"/api/events/{sample_event.id}/enrollments", headers=ngo_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["total"] == 1
    assert data["enrollments"][0]["volunteer_email"] == "volunteer@test.com"
