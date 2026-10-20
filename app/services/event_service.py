"""Event management and enrollment service."""

from datetime import date
from ..extensions import db
from ..models.event import Event
from ..models.enrollment import Enrollment
from ..models.volunteer import Volunteer


def filter_events(
    city: str | None = None,
    category: str | None = None,
    status: str | None = "active",
    search: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    per_page: int = 12,
):
    """Filter and paginate events."""
    query = Event.query

    if status:
        query = query.filter_by(status=status)
    if city:
        query = query.filter(Event.city.ilike(f"%{city}%"))
    if category:
        query = query.filter(Event.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(
            (Event.title.ilike(f"%{search}%")) | (Event.description.ilike(f"%{search}%"))
        )
    if date_from:
        try:
            query = query.filter(Event.event_date >= date.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(Event.event_date <= date.fromisoformat(date_to))
        except ValueError:
            pass

    return query.order_by(Event.event_date.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )


def enroll_volunteer(volunteer_id: int, event_id: int) -> tuple[Enrollment | None, str | None, int]:
    """Enroll a volunteer into an event with transaction safety and capacity validation."""
    event = Event.query.get(event_id)
    if not event:
        return None, "Event not found", 404

    volunteer = Volunteer.query.get(volunteer_id)
    if not volunteer:
        return None, "Volunteer not found", 404

    if event.status != "active":
        return None, "Event is not accepting enrollments", 400

    if event.event_date < date.today():
        return None, "Cannot enroll in past events", 400

    if event.max_volunteers and event.enrolled_count() >= event.max_volunteers:
        return None, "Event has reached maximum capacity", 400

    existing = Enrollment.query.filter_by(volunteer_id=volunteer_id, event_id=event_id).first()
    if existing:
        return None, "Volunteer is already enrolled in this event", 409

    enrollment = Enrollment(volunteer_id=volunteer_id, event_id=event_id)
    db.session.add(enrollment)
    db.session.commit()

    return enrollment, None, 201


def unenroll_volunteer(volunteer_id: int, event_id: int) -> tuple[bool, str | None, int]:
    """Unenroll a volunteer from an event."""
    enrollment = Enrollment.query.filter_by(volunteer_id=volunteer_id, event_id=event_id).first()
    if not enrollment:
        return False, "Not enrolled in this event", 404

    if enrollment.attended:
        return False, "Cannot unenroll from an event you have already attended", 400

    db.session.delete(enrollment)
    db.session.commit()
    return True, None, 200
