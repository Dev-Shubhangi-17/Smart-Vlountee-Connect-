"""NGO routes — list, detail, own profile, own events, stats."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from ..extensions import db
from ..models.ngo import NGO
from ..models.event import Event

ngos_bp = Blueprint("ngos", __name__)


def _get_current_ngo():
    """Return the currently authenticated NGO or error tuple."""
    claims = get_jwt()
    if claims.get("role") != "ngo":
        return None, (jsonify({"error": "Access restricted to NGOs"}), 403)
    user_id = get_jwt_identity()
    pk = int(user_id) if str(user_id).isdigit() else user_id
    ngo = db.session.get(NGO, pk)
    if not ngo:
        return None, (jsonify({"error": "NGO not found"}), 404)
    return ngo, None


# ---------------------------------------------------------------------------
# Public Endpoints
# ---------------------------------------------------------------------------

from .auth import ngo_register

@ngos_bp.route("", methods=["GET", "POST"])
def list_or_register_ngos():
    """List all verified NGOs or register a new one.

    Query params (GET):
        city, cause_area, search, page (default 1), per_page (default 12)
    """
    if request.method == "POST":
        return ngo_register()

    city = request.args.get("city")
    cause_area = request.args.get("cause_area")
    search = request.args.get("search")
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 12)), 50)

    query = NGO.query.filter_by(is_active=True)

    if city:
        query = query.filter(NGO.city.ilike(f"%{city}%"))
    if cause_area:
        query = query.filter(NGO.cause_areas.ilike(f"%{cause_area}%"))
    if search:
        query = query.filter(NGO.name.ilike(f"%{search}%"))

    paginated = query.order_by(NGO.verified.desc(), NGO.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "ngos": [ngo.to_dict() for ngo in paginated.items],
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": paginated.page,
    }), 200


@ngos_bp.route("/<int:ngo_id>", methods=["GET"])
def get_ngo(ngo_id):
    """Get a single NGO by ID."""
    ngo = db.session.get(NGO, ngo_id)
    if not ngo:
        return jsonify({"error": "NGO not found"}), 404
    return jsonify(ngo.to_dict()), 200


@ngos_bp.route("/<int:ngo_id>/events", methods=["GET"])
def get_ngo_events(ngo_id):
    """Get all active events for a specific NGO."""
    ngo = db.session.get(NGO, ngo_id)
    if not ngo:
        return jsonify({"error": "NGO not found"}), 404
    events = ngo.events.filter_by(status="active").order_by(Event.event_date.asc()).all()
    return jsonify({"events": [e.to_dict() for e in events], "total": len(events)}), 200


# ---------------------------------------------------------------------------
# Protected Endpoints (NGO must be logged in)
# ---------------------------------------------------------------------------

@ngos_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_profile():
    """Get the authenticated NGO's own profile."""
    ngo, err = _get_current_ngo()
    if err:
        return err
    return jsonify(ngo.to_dict(include_private=True)), 200


@ngos_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_my_profile():
    """Update the authenticated NGO's profile.

    Body (JSON — all optional):
        name, phone, city, state, address, website, description, cause_areas, logo_url
    """
    ngo, err = _get_current_ngo()
    if err:
        return err

    data = request.get_json(silent=True) or {}

    if "name" in data:
        ngo.name = data["name"].strip()
    if "phone" in data:
        ngo.phone = data["phone"]
    if "city" in data:
        ngo.city = data["city"]
    if "state" in data:
        ngo.state = data["state"]
    if "address" in data:
        ngo.address = data["address"]
    if "website" in data:
        ngo.website = data["website"]
    if "description" in data:
        ngo.description = data["description"]
    if "cause_areas" in data:
        ca = data["cause_areas"]
        ngo.cause_areas = ",".join(ca) if isinstance(ca, list) else str(ca or "")
    if "logo_url" in data:
        ngo.logo_url = data["logo_url"]

    db.session.commit()
    return jsonify({"message": "Profile updated!", "ngo": ngo.to_dict(include_private=True)}), 200


@ngos_bp.route("/me/events", methods=["GET"])
@jwt_required()
def get_my_events():
    """Get all events created by the authenticated NGO."""
    ngo, err = _get_current_ngo()
    if err:
        return err

    status_filter = request.args.get("status")  # active | completed | cancelled
    query = ngo.events

    if status_filter:
        query = query.filter_by(status=status_filter)

    events = query.order_by(Event.event_date.desc()).all()
    return jsonify({"events": [e.to_dict() for e in events], "total": len(events)}), 200


@ngos_bp.route("/me/stats", methods=["GET"])
@jwt_required()
def get_my_stats():
    """Return NGO dashboard analytics."""
    ngo, err = _get_current_ngo()
    if err:
        return err

    all_events = ngo.events.all()
    total_events = len(all_events)
    active_events = ngo.events.filter_by(status="active").count()
    completed_events = ngo.events.filter_by(status="completed").count()

    total_volunteers = 0
    total_attended = 0
    total_hours_contributed = 0
    total_feedback = 0
    rating_sum = 0

    for event in all_events:
        enrollments = event.enrollments.all()
        total_volunteers += len(enrollments)
        attended = [e for e in enrollments if e.attended]
        total_attended += len(attended)
        total_hours_contributed += sum(e.hours_logged for e in attended if e.hours_logged)

        feedbacks = event.feedback.all()
        total_feedback += len(feedbacks)
        rating_sum += sum(f.rating for f in feedbacks)

    avg_rating = round(rating_sum / total_feedback, 1) if total_feedback > 0 else None

    return jsonify({
        "ngo_id": ngo.id,
        "name": ngo.name,
        "total_events": total_events,
        "active_events": active_events,
        "completed_events": completed_events,
        "total_volunteers_enrolled": total_volunteers,
        "total_volunteers_attended": total_attended,
        "total_volunteer_hours": total_hours_contributed,
        "total_feedback_received": total_feedback,
        "average_rating": avg_rating,
    }), 200
