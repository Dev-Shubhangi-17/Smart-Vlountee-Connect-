"""Platform-wide statistics — used by the hero section and analytics dashboards on the frontend."""

from flask import Blueprint, jsonify
from ..models.volunteer import Volunteer
from ..models.ngo import NGO
from ..models.event import Event
from ..models.enrollment import Enrollment
from ..services.stats_service import get_platform_analytics

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
            "active_events": int,
            "total_enrollments": int,
            "total_hours_volunteered": float,
            "total_certificates_issued": int
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
    total_certificates = Enrollment.query.filter_by(certificate_issued=True).count()

    return jsonify({
        "total_volunteers": total_volunteers,
        "total_ngos": total_ngos,
        "total_events": total_events,
        "active_events": active_events,
        "total_enrollments": total_enrollments,
        "total_hours_volunteered": round(total_hours, 1),
        "total_certificates_issued": total_certificates,
    }), 200


@stats_bp.route("/analytics", methods=["GET"])
def get_analytics():
    """Return platform analytics breakdown for charts."""
    return jsonify(get_platform_analytics()), 200
