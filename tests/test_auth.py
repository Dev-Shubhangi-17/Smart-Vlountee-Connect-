"""Tests for volunteer and NGO authentication, passwords, tokens, and current user."""

from app.models.volunteer import Volunteer
from app.models.ngo import NGO
from app.extensions import bcrypt


def test_volunteer_registration_success(client, db_session):
    """Test successful volunteer registration and password hashing."""
    payload = {
        "name": "Aarav Patel",
        "email": "aarav@example.com",
        "password": "SecretPassword123",
        "phone": "+91 9876500000",
        "city": "Pune",
        "interests": ["Environment", "Education"],
        "availability": "Weekends"
    }
    res = client.post("/api/auth/volunteer/register", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert "access_token" in data
    assert data["role"] == "volunteer"
    assert data["volunteer"]["email"] == "aarav@example.com"

    # Verify password was hashed and not plaintext
    vol = Volunteer.query.filter_by(email="aarav@example.com").first()
    assert vol is not None
    assert vol.password_hash != "SecretPassword123"
    assert bcrypt.check_password_hash(vol.password_hash, "SecretPassword123")


def test_volunteer_registration_missing_fields(client, db_session):
    """Test missing required fields returns 400."""
    res = client.post("/api/auth/volunteer/register", json={"email": "incomplete@test.com"})
    assert res.status_code == 400
    assert "Missing required fields" in res.get_json()["error"]


def test_volunteer_registration_duplicate_email(client, db_session, sample_volunteer):
    """Test duplicate volunteer email returns 409."""
    payload = {
        "name": "Duplicate User",
        "email": sample_volunteer.email,
        "password": "password123"
    }
    res = client.post("/api/auth/volunteer/register", json=payload)
    assert res.status_code == 409
    assert "already exists" in res.get_json()["error"]


def test_volunteer_registration_weak_password(client, db_session):
    """Test short password rejected."""
    payload = {
        "name": "Weak Pass",
        "email": "weak@example.com",
        "password": "123"
    }
    res = client.post("/api/auth/volunteer/register", json=payload)
    assert res.status_code == 400
    assert "at least 6 characters" in res.get_json()["error"]


def test_volunteer_login_success(client, db_session, sample_volunteer):
    """Test successful volunteer login."""
    res = client.post("/api/auth/volunteer/login", json={
        "email": sample_volunteer.email,
        "password": "password123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert data["role"] == "volunteer"


def test_volunteer_login_wrong_password(client, db_session, sample_volunteer):
    """Test volunteer login with incorrect password returns 401."""
    res = client.post("/api/auth/volunteer/login", json={
        "email": sample_volunteer.email,
        "password": "wrongpassword"
    })
    assert res.status_code == 401
    assert "Invalid email or password" in res.get_json()["error"]


def test_ngo_registration_and_login(client, db_session):
    """Test NGO registration and subsequent login."""
    reg_payload = {
        "name": "Helpage Foundation",
        "email": "contact@helpage.org",
        "password": "NGOPassword123",
        "registration_number": "NGO-MH-2024-9988",
        "city": "Mumbai",
        "cause_areas": ["Healthcare", "Elderly Care"]
    }
    reg_res = client.post("/api/auth/ngo/register", json=reg_payload)
    assert reg_res.status_code == 201
    data = reg_res.get_json()
    assert data["role"] == "ngo"
    assert data["ngo"]["registration_number"] == "NGO-MH-2024-9988"

    # Login
    login_res = client.post("/api/auth/ngo/login", json={
        "email": "contact@helpage.org",
        "password": "NGOPassword123"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.get_json()


def test_get_current_user_me(client, db_session, volunteer_headers, ngo_headers):
    """Test GET /api/auth/me for volunteer and NGO."""
    # Volunteer
    res_vol = client.get("/api/auth/me", headers=volunteer_headers)
    assert res_vol.status_code == 200
    data_vol = res_vol.get_json()
    assert data_vol["role"] == "volunteer"
    assert data_vol["user"]["email"] == "volunteer@test.com"

    # NGO
    res_ngo = client.get("/api/auth/me", headers=ngo_headers)
    assert res_ngo.status_code == 200
    data_ngo = res_ngo.get_json()
    assert data_ngo["role"] == "ngo"
    assert data_ngo["user"]["email"] == "ngo@test.com"

    # Unauthenticated
    res_anon = client.get("/api/auth/me")
    assert res_anon.status_code == 401


def test_logout(client):
    """Test logout endpoint."""
    res = client.post("/api/auth/logout")
    assert res.status_code == 200
    assert "Logged out successfully" in res.get_json()["message"]
