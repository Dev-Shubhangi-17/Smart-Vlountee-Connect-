"""Platform analytics and dashboard statistics service."""

from collections import Counter
from ..extensions import db
from ..models.volunteer import Volunteer
from ..models.ngo import NGO
from ..models.event import Event
from ..models.enrollment import Enrollment


def get_platform_metrics() -> dict:
    """Return aggregated platform statistics."""
    total_volunteers = Volunteer.query.filter_by(is_active=True).count()
    total_ngos = NGO.query.filter_by(is_active=True).count()
    total_events = Event.query.count()
    active_events = Event.query.filter_by(status="active").count()
    total_enrollments = Enrollment.query.count()

    attended = Enrollment.query.filter_by(attended=True).all()
    total_hours = sum(e.hours_logged for e in attended if e.hours_logged)
    total_certificates = Enrollment.query.filter_by(certificate_issued=True).count()

    return {
        "total_volunteers": total_volunteers,
        "total_ngos": total_ngos,
        "total_events": total_events,
        "active_events": active_events,
        "total_enrollments": total_enrollments,
        "total_hours_volunteered": round(total_hours, 1),
        "total_certificates_issued": total_certificates,
    }


def get_platform_analytics() -> dict:
    """Return analytics data for charts and demographic breakdowns."""
    # Count events by category
    events = Event.query.all()
    category_counts = Counter(e.category for e in events if e.category)

    # Count volunteers by availability
    volunteers = Volunteer.query.filter_by(is_active=True).all()
    availability_counts = Counter(v.availability for v in volunteers if v.availability)

    return {
        "categories": dict(category_counts),
        "availability": dict(availability_counts),
        "metrics": get_platform_metrics(),
    }
