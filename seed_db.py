"""Seed script to populate database with initial sample NGOs and Events."""

from app import create_app
from app.extensions import db, bcrypt
from app.models.ngo import NGO
from app.models.event import Event
from app.models.volunteer import Volunteer
from datetime import date, time

app = create_app()

with app.app_context():
    # Only seed if empty
    if NGO.query.count() == 0:
        print("Seeding sample NGOs...")
        ngo1 = NGO(
            name="GreenIndia Foundation",
            email="contact@greenindia.org",
            password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
            registration_number="NGO-MH-2021-0042",
            phone="+91 9876543210",
            city="Mumbai",
            state="Maharashtra",
            website="https://greenindia.org",
            description="Dedicated to urban afforestation and forest conservation across Maharashtra.",
            cause_areas="Environment,Tree Plantation",
            verified=True
        )

        ngo2 = NGO(
            name="LifeSavers Trust",
            email="info@lifesaverstrust.org",
            password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
            registration_number="NGO-DL-2020-0118",
            phone="+91 9811223344",
            city="Delhi",
            state="Delhi",
            website="https://lifesaverstrust.org",
            description="Organizing voluntary blood donation drives across major Indian metros.",
            cause_areas="Blood Donation,Healthcare",
            verified=True
        )

        ngo3 = NGO(
            name="EduReach India",
            email="hello@edureach.org",
            password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
            registration_number="NGO-MH-2019-0951",
            phone="+91 9765432109",
            city="Mumbai",
            state="Maharashtra",
            website="https://edureach.org",
            description="Empowering underprivileged children through quality weekend education.",
            cause_areas="Education,Child Welfare",
            verified=True
        )

        db.session.add_all([ngo1, ngo2, ngo3])
        db.session.commit()
        print("NGOs seeded successfully!")

        print("Seeding sample Events...")
        event1 = Event(
            ngo_id=ngo1.id,
            title="City Forest Tree Plantation Drive",
            description="Join us to plant 500 saplings in the Aarey forest region to restore urban greenery.",
            category="Environment",
            city="Mumbai",
            venue="Aarey Forest, Goregaon East, Mumbai",
            event_date=date(2026, 9, 15),
            start_time=time(7, 0),
            duration_hours=4.0,
            max_volunteers=50,
            status="active"
        )

        event2 = Event(
            ngo_id=ngo2.id,
            title="Mega Blood Donation Camp 2026",
            description="Donate blood and help save lives. Free health check-up and refreshments provided.",
            category="Blood Donation",
            city="Delhi",
            venue="Rajiv Gandhi Community Hall, New Delhi",
            event_date=date(2026, 9, 20),
            start_time=time(9, 0),
            duration_hours=6.0,
            max_volunteers=200,
            status="active"
        )

        event3 = Event(
            ngo_id=ngo3.id,
            title="Weekend Tuition Drive for Children",
            description="Volunteer to teach basic mathematics, science, and English to primary school students.",
            category="Education",
            city="Mumbai",
            venue="Dharavi Community Center, Mumbai",
            event_date=date(2026, 9, 25),
            start_time=time(10, 0),
            duration_hours=3.0,
            max_volunteers=30,
            status="active"
        )

        db.session.add_all([event1, event2, event3])
        db.session.commit()
        print("Events seeded successfully!")
    else:
        print("Database already contains data, skipping seed.")
