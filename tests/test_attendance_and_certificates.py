"""Tests for attendance tracking, volunteer hours calculation, and certificates."""

from app.models.volunteer import Volunteer


def test_ngo_record_attendance_and_hours(client, db_session, ngo_headers, volunteer_headers, sample_event, sample_volunteer):
    """Test NGO marking attendance, issuing certificates, and updating volunteer total hours."""
    # Volunteer enrolls
    enr_res = client.post(f"/api/events/{sample_event.id}/enroll", headers=volunteer_headers)
    enrollment_id = enr_res.get_json()["enrollment"]["id"]

    # NGO records attendance with 4.5 hours and certificate
    att_res = client.post(f"/api/events/{sample_event.id}/attendance", json={
        "enrollment_id": enrollment_id,
        "attended": True,
        "hours_logged": 4.5,
        "certificate_issued": True
    }, headers=ngo_headers)
    assert att_res.status_code == 200
    data = att_res.get_json()
    assert data["enrollment"]["attended"] is True
    assert data["enrollment"]["hours_logged"] == 4.5
    assert data["enrollment"]["certificate_issued"] is True

    # Check volunteer total hours updated in DB
    vol = db_session.get(Volunteer, sample_volunteer.id)
    assert vol.total_hours == 4.5

    # Check volunteer can view certificates
    certs_res = client.get("/api/volunteers/me/certificates", headers=volunteer_headers)
    assert certs_res.status_code == 200
    assert certs_res.get_json()["total"] == 1

    # Attended event cannot be unenrolled
    unenroll_res = client.delete(f"/api/events/{sample_event.id}/enroll", headers=volunteer_headers)
    assert unenroll_res.status_code == 400
    assert "already attended" in unenroll_res.get_json()["error"]
