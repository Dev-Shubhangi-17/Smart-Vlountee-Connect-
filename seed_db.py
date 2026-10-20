"""Seed script to populate database with comprehensive sample data for development and demonstration."""

from datetime import date, time, timedelta
from app.extensions import db, bcrypt
from app.models.ngo import NGO
from app.models.event import Event
from app.models.volunteer import Volunteer
from app.models.enrollment import Enrollment
from app.models.feedback import Feedback
from app.models.contact import ContactMessage


def seed_data():
    """Populate database with sample data if empty."""
    if NGO.query.count() == 0:
        print("[*] Seeding sample NGOs...")
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

        ngo4 = NGO(
            name="AnimalAid India",
            email="support@animalaid.org",
            password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
            registration_number="NGO-KA-2022-0774",
            phone="+91 9988776655",
            city="Bangalore",
            state="Karnataka",
            website="https://animalaid.org",
            description="Rescue, rehabilitation, and medical care for stray animals.",
            cause_areas="Animal Rescue,Animal Welfare",
            verified=True
        )

        db.session.add_all([ngo1, ngo2, ngo3, ngo4])
        db.session.commit()
        print("[OK] NGOs seeded successfully!")

        print("[*] Seeding sample Volunteers...")
        vol1 = Volunteer(
            name="Riya Sharma",
            email="riya@example.com",
            password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
            phone="+91 9820011223",
            city="Mumbai",
            bio="Software engineer passionate about tree plantation and environmental sustainability.",
            interests="Environment,Tree Plantation,Education",
            availability="Weekends",
            total_hours=4.0,
            is_active=True
        )

        vol2 = Volunteer(
            name="Arjun Mehta",
            email="arjun@example.com",
            password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
            phone="+91 9810099887",
            city="Delhi",
            bio="Pre-med student eager to support medical and blood donation initiatives.",
            interests="Blood Donation,Healthcare",
            availability="Weekends",
            total_hours=5.0,
            is_active=True
        )

        vol3 = Volunteer(
            name="Kavita Deshmukh",
            email="kavita@example.com",
            password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
            phone="+91 9890044556",
            city="Mumbai",
            bio="High school teacher helping with youth literacy and animal rescue drives.",
            interests="Education,Animal Rescue",
            availability="Weekdays",
            total_hours=0.0,
            is_active=True
        )

        db.session.add_all([vol1, vol2, vol3])
        db.session.commit()
        print("[OK] Volunteers seeded successfully!")

        print("[*] Seeding sample Events...")
        today = date.today()
        event1 = Event(
            ngo_id=ngo1.id,
            title="City Forest Tree Plantation Drive",
            description="Join us to plant 500 native saplings in the Aarey forest region to restore urban greenery and biodiversity.",
            category="Environment",
            city="Mumbai",
            venue="Aarey Forest, Goregaon East, Mumbai",
            event_date=today + timedelta(days=14),
            start_time=time(7, 0),
            duration_hours=4.0,
            max_volunteers=50,
            status="active"
        )

        event2 = Event(
            ngo_id=ngo2.id,
            title="Mega Blood Donation Camp 2026",
            description="Donate blood and help save lives. Full medical supervision, health check-up, and refreshments provided.",
            category="Blood Donation",
            city="Delhi",
            venue="Rajiv Gandhi Community Hall, New Delhi",
            event_date=today + timedelta(days=21),
            start_time=time(9, 0),
            duration_hours=6.0,
            max_volunteers=200,
            status="active"
        )

        event3 = Event(
            ngo_id=ngo3.id,
            title="Weekend Tuition Drive for Underprivileged Kids",
            description="Volunteer to teach mathematics, basic science, and conversational English to primary school students.",
            category="Education",
            city="Mumbai",
            venue="Dharavi Community Center, Mumbai",
            event_date=today + timedelta(days=7),
            start_time=time(10, 0),
            duration_hours=3.0,
            max_volunteers=30,
            status="active"
        )

        event4 = Event(
            ngo_id=ngo4.id,
            title="Street Dog Vaccination and Health Camp",
            description="Assist veterinarians with stray dog check-ups, rabies vaccinations, and distribution of healthy meals.",
            category="Animal Rescue",
            city="Bangalore",
            venue="Cubbon Park Area, Bangalore",
            event_date=today + timedelta(days=10),
            start_time=time(8, 30),
            duration_hours=4.0,
            max_volunteers=25,
            status="active"
        )

        event5 = Event(
            ngo_id=ngo1.id,
            title="Coastal Mangrove Clean-up Drive",
            description="Successful coastal mangrove debris collection and plantation along the Mahim coastline.",
            category="Environment",
            city="Mumbai",
            venue="Mahim Beach & Mangroves, Mumbai",
            event_date=today - timedelta(days=15),
            start_time=time(6, 30),
            duration_hours=4.0,
            max_volunteers=40,
            status="completed"
        )

        event6 = Event(
            ngo_id=ngo2.id,
            title="Emergency Hospital Blood Drive",
            description="Rapid-response voluntary blood donation camp organized for regional trauma care centers.",
            category="Blood Donation",
            city="Delhi",
            venue="AIIMS Campus Blood Bank, New Delhi",
            event_date=today - timedelta(days=30),
            start_time=time(9, 0),
            duration_hours=5.0,
            max_volunteers=80,
            status="completed"
        )

        db.session.add_all([event1, event2, event3, event4, event5, event6])
        db.session.commit()
        print("[OK] Events seeded successfully!")

        print("[*] Seeding Enrollments, Attendance & Certificates...")
        enr1 = Enrollment(
            volunteer_id=vol1.id,
            event_id=event1.id,
            attended=False,
            hours_logged=0.0
        )
        enr2 = Enrollment(
            volunteer_id=vol1.id,
            event_id=event5.id,
            attended=True,
            hours_logged=4.0,
            certificate_issued=True,
            certificate_url="/certificates/cert_riya_mangrove.pdf"
        )
        enr3 = Enrollment(
            volunteer_id=vol2.id,
            event_id=event2.id,
            attended=False,
            hours_logged=0.0
        )
        enr4 = Enrollment(
            volunteer_id=vol2.id,
            event_id=event6.id,
            attended=True,
            hours_logged=5.0,
            certificate_issued=True,
            certificate_url="/certificates/cert_arjun_blood.pdf"
        )
        enr5 = Enrollment(
            volunteer_id=vol3.id,
            event_id=event3.id,
            attended=False,
            hours_logged=0.0
        )

        db.session.add_all([enr1, enr2, enr3, enr4, enr5])
        db.session.commit()
        print("[OK] Enrollments seeded successfully!")

        print("[*] Seeding Feedback & Reviews...")
        fb1 = Feedback(
            volunteer_id=vol1.id,
            event_id=event5.id,
            rating=5,
            review_text="Fantastic initiative! Great team coordination and meaningful impact on the mangroves."
        )
        fb2 = Feedback(
            volunteer_id=vol2.id,
            event_id=event6.id,
            rating=5,
            review_text="Very well organized by LifeSavers Trust. High hygienic standards and supportive staff."
        )
        db.session.add_all([fb1, fb2])
        db.session.commit()
        print("[OK] Feedback seeded successfully!")

        print("[*] Seeding Contact Messages...")
        msg1 = ContactMessage(
            name="Vikram Sethi",
            email="vikram@corporate.com",
            subject="Corporate CSR Partnership",
            message="We would like to connect our 500-member engineering team to volunteer for environmental causes.",
            is_read=False
        )
        db.session.add(msg1)
        db.session.commit()
        print("[OK] Contact messages seeded successfully!")

        print("[SUCCESS] Database fully initialized with realistic demonstration data!")
    else:
        print("[INFO] Database already contains data. Skipping seed.")


if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_data()

