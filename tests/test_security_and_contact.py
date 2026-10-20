"""Tests for security, invalid/tampered tokens, and contact form."""

def test_tampered_token_rejected(client, db_session):
    """Test corrupted or invalid JWT token is rejected with 401."""
    headers = {
        "Authorization": "Bearer invalid.jwt.token",
        "Content-Type": "application/json"
    }
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 401
    assert res.get_json()["code"] == "invalid_token"


def test_missing_token_rejected(client, db_session):
    """Test protected route without Authorization header returns 401."""
    res = client.get("/api/volunteers/me")
    assert res.status_code == 401
    assert res.get_json()["code"] == "authorization_required"


def test_role_segregation(client, db_session, volunteer_headers, ngo_headers):
    """Test volunteer cannot access NGO routes and vice-versa."""
    # Volunteer trying to access NGO stats
    res_vol = client.get("/api/ngos/me/stats", headers=volunteer_headers)
    assert res_vol.status_code == 403

    # NGO trying to access Volunteer stats
    res_ngo = client.get("/api/volunteers/me/stats", headers=ngo_headers)
    assert res_ngo.status_code == 403


def test_contact_form_submission(client, db_session):
    """Test contact message submission and validation."""
    payload = {
        "name": "Meera Sen",
        "email": "meera@example.com",
        "subject": "Volunteer Inquiry",
        "message": "Interested in participating in tree plantation drives."
    }
    res = client.post("/api/contact", json=payload)
    assert res.status_code == 201
    assert "Thank you for reaching out" in res.get_json()["message"]

    # Verify listing contact messages
    list_res = client.get("/api/contact")
    assert list_res.status_code == 200
    assert list_res.get_json()["total"] == 1


def test_contact_form_invalid_email(client, db_session):
    """Test contact form with invalid email returns 400."""
    res = client.post("/api/contact", json={
        "name": "Bad Email",
        "email": "not-an-email",
        "message": "Hello"
    })
    assert res.status_code == 400
    assert "valid email" in res.get_json()["error"]
