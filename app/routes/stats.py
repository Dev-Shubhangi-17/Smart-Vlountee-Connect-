"""Platform-wide statistics — used by the hero section on the frontend."""

from flask import Blueprint, jsonify
from ..models.volunteer import Volunteer
from ..models.ngo import NGO
from ..models.event import Event
from ..models.enrollment import Enrollment

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("", methods=["GET"])
@stats_bp.route("/dashboard/stats", methods=["GET"])
def get_platform_stats():
    """Return aggregated platform statistics for the homepage.

    Response:
        {
            "total_volunteers": int,
            "total_ngos": int,
            "total_events": int,
            "total_hours_volunteered": float,
            "total_enrollments": int
        }
    """
    total_volunteers = Volunteer.query.filter_by(is_active=True).count()
    total_ngos = NGO.query.filter_by(is_active=True).count()
    total_events = Event.query.count()
    active_events = Event.query.filter_by(status="active").count()
    total_enrollments = Enrollment.query.count()

    # Total volunteer hours across all attended enrollments
    attended = Enrollment.query.filter_by(attended=True).all()
    total_hours = sum(e.hours_logged for e in attended if e.hours_logged)

    return jsonify({
        "total_volunteers": total_volunteers,
        "total_ngos": total_ngos,
        "total_events": total_events,
        "active_events": active_events,
        "total_enrollments": total_enrollments,
        "total_hours_volunteered": round(total_hours, 1),
    }), 200
