"""Pytest configuration and fixtures with isolated in-memory database."""

import pytest
from datetime import date, time, timedelta
from app import create_app
from app.extensions import db as _db, bcrypt
from app.models.volunteer import Volunteer
from app.models.ngo import NGO
from app.models.event import Event
from app.models.enrollment import Enrollment


@pytest.fixture(scope="session")
def app():
    """Create and configure a testing Flask app."""
    application = create_app("testing")
    return application


@pytest.fixture(scope="function")
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """Create fresh database tables for each test and drop afterwards."""
    with app.app_context():
        _db.create_all()
        yield _db.session
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def sample_volunteer(db_session):
    """Create a sample volunteer."""
    vol = Volunteer(
        name="Test Volunteer",
        email="volunteer@test.com",
        password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
        phone="+91 9999900001",
        city="Mumbai",
        bio="Passionate community volunteer",
        interests="Environment,Education",
        availability="Weekends",
        total_hours=0.0,
        is_active=True
    )
    db_session.add(vol)
    db_session.commit()
    return vol


@pytest.fixture
def sample_ngo(db_session):
    """Create a sample NGO."""
    ngo = NGO(
        name="Test NGO Foundation",
        email="ngo@test.com",
        password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
        registration_number="REG-TEST-001",
        phone="+91 9999900002",
        city="Mumbai",
        state="Maharashtra",
        description="Non-profit focused on green initiatives",
        cause_areas="Environment,Tree Plantation",
        verified=True,
        is_active=True
    )
    db_session.add(ngo)
    db_session.commit()
    return ngo


@pytest.fixture
def sample_event(db_session, sample_ngo):
    """Create a sample active upcoming event."""
    evt = Event(
        ngo_id=sample_ngo.id,
        title="Sample Tree Plantation Drive",
        description="Planting trees in the community",
        category="Environment",
        city="Mumbai",
        venue="Green Park, Mumbai",
        event_date=date.today() + timedelta(days=7),
        start_time=time(8, 0),
        duration_hours=4.0,
        max_volunteers=20,
        status="active"
    )
    db_session.add(evt)
    db_session.commit()
    return evt


@pytest.fixture
def volunteer_headers(client, sample_volunteer):
    """Login sample volunteer and return authorization headers."""
    res = client.post("/api/auth/volunteer/login", json={
        "email": "volunteer@test.com",
        "password": "password123"
    })
    token = res.get_json()["access_token"]
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def ngo_headers(client, sample_ngo):
    """Login sample NGO and return authorization headers."""
    res = client.post("/api/auth/ngo/login", json={
        "email": "ngo@test.com",
        "password": "password123"
    })
    token = res.get_json()["access_token"]
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
