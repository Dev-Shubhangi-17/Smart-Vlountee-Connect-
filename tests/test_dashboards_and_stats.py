"""Tests for volunteer/NGO dashboards, platform statistics, and analytics."""

from datetime import date, timedelta
from app.models.enrollment import Enrollment


def test_empty_database_stats(client, db_session):
    """Test platform stats on an empty database."""
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_volunteers"] == 0
    assert data["total_ngos"] == 0
    assert data["total_events"] == 0
    assert data["total_hours_volunteered"] == 0.0


def test_volunteer_dashboard_stats(client, db_session, volunteer_headers, sample_volunteer, sample_event):
    """Test volunteer personal dashboard metrics."""
    # Enroll and mark attended
    enr = Enrollment(volunteer_id=sample_volunteer.id, event_id=sample_event.id, attended=True, hours_logged=3.0, certificate_issued=True)
    db_session.add(enr)
    db_session.commit()

    res = client.get("/api/volunteers/me/stats", headers=volunteer_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_enrolled"] == 1
    assert data["total_attended"] == 1
    assert data["total_hours"] == 3.0
    assert data["total_certificates"] == 1


def test_ngo_dashboard_stats(client, db_session, ngo_headers, sample_volunteer, sample_event):
    """Test NGO dashboard metrics calculated from events and enrollments."""
    enr = Enrollment(volunteer_id=sample_volunteer.id, event_id=sample_event.id, attended=True, hours_logged=4.0)
    db_session.add(enr)
    db_session.commit()

    res = client.get("/api/ngos/me/stats", headers=ngo_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_events"] == 1
    assert data["total_volunteers_enrolled"] == 1
    assert data["total_volunteers_attended"] == 1
    assert data["total_volunteer_hours"] == 4.0


def test_platform_analytics(client, db_session, sample_event, sample_volunteer):
    """Test platform analytics category breakdown and metrics."""
    res = client.get("/api/stats/analytics")
    assert res.status_code == 200
    data = res.get_json()
    assert "categories" in data
    assert "metrics" in data
    assert data["metrics"]["total_volunteers"] == 1
