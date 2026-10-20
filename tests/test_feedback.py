"""Tests for post-event feedback and ratings."""

from app.models.enrollment import Enrollment


def test_feedback_submission_and_rating_calculation(client, db_session, ngo_headers, volunteer_headers, sample_event, sample_volunteer):
    """Test feedback submission for attended event, rating calculation, and duplicate prevention."""
    # Volunteer enrolls
    enr = Enrollment(volunteer_id=sample_volunteer.id, event_id=sample_event.id, attended=True)
    db_session.add(enr)
    db_session.commit()

    # Submit feedback
    fb_res = client.post(f"/api/events/{sample_event.id}/feedback", json={
        "rating": 5,
        "review_text": "Incredible initiative and very well coordinated!"
    }, headers=volunteer_headers)
    assert fb_res.status_code == 201
    assert fb_res.get_json()["feedback"]["rating"] == 5

    # Public feedback endpoint
    get_fb = client.get(f"/api/events/{sample_event.id}/feedback")
    assert get_fb.status_code == 200
    assert get_fb.get_json()["total_reviews"] == 1
    assert get_fb.get_json()["avg_rating"] == 5.0

    # Duplicate feedback prevention
    fb_dup = client.post(f"/api/events/{sample_event.id}/feedback", json={
        "rating": 4,
        "review_text": "Trying again"
    }, headers=volunteer_headers)
    assert fb_dup.status_code == 409
    assert "already submitted" in fb_dup.get_json()["error"]


def test_feedback_without_attendance_rejected(client, db_session, volunteer_headers, sample_event):
    """Test volunteer cannot submit feedback if they did not attend the event."""
    res = client.post(f"/api/events/{sample_event.id}/feedback", json={
        "rating": 5,
        "review_text": "Did not attend"
    }, headers=volunteer_headers)
    assert res.status_code == 403
    assert "only leave feedback for events you have attended" in res.get_json()["error"]


def test_feedback_invalid_rating_bounds(client, db_session, volunteer_headers, sample_event, sample_volunteer):
    """Test rating must be between 1 and 5."""
    enr = Enrollment(volunteer_id=sample_volunteer.id, event_id=sample_event.id, attended=True)
    db_session.add(enr)
    db_session.commit()

    res_zero = client.post(f"/api/events/{sample_event.id}/feedback", json={"rating": 0}, headers=volunteer_headers)
    assert res_zero.status_code == 400

    res_six = client.post(f"/api/events/{sample_event.id}/feedback", json={"rating": 6}, headers=volunteer_headers)
    assert res_six.status_code == 400
