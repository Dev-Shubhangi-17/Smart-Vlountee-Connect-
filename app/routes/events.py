"""Events routes — CRUD for events, enrollment, attendance, feedback."""

from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.event import Event
from ..models.ngo import NGO
from ..models.enrollment import Enrollment
from ..models.feedback import Feedback
from ..models.volunteer import Volunteer

events_bp = Blueprint("events", __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _optional_jwt():
    """Try to load JWT but don't fail if not present. Returns (identity, claims) or (None, {})."""
    try:
        verify_jwt_in_request(optional=True)
        return get_jwt_identity(), get_jwt()
    except Exception:
        return None, {}


# ---------------------------------------------------------------------------
# Public: List and Get Events
# ---------------------------------------------------------------------------

@events_bp.route("", methods=["GET"])
def list_events():
    """List events with optional filtering.

    Query params:
        city, category, status (default=active), search,
        date_from, date_to, page (default 1), per_page (default 12)
    """
    city = request.args.get("city")
    category = request.args.get("category")
    status = request.args.get("status", "active")
    search = request.args.get("search")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 12)), 50)

    query = Event.query

    if status and status != "all":
        query = query.filter_by(status=status)
    if city:
        query = query.filter(Event.city.ilike(f"%{city}%"))
    if category and category != "all":
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

    paginated = query.order_by(Event.event_date.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "events": [e.to_dict() for e in paginated.items],
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": paginated.page,
    }), 200


@events_bp.route("/<int:event_id>", methods=["GET"])
def get_event(event_id):
    """Get a single event by ID (with full details)."""
    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(event.to_dict()), 200


# ---------------------------------------------------------------------------
# NGO: Create, Update, Delete Events
# ---------------------------------------------------------------------------

@events_bp.route("", methods=["POST"])
@jwt_required()
def create_event():
    """Create a new event. Requires NGO JWT.

    Body (JSON):
        title*, event_date* (YYYY-MM-DD), category, city, venue,
        description, start_time (HH:MM), duration_hours, max_volunteers, image_url
    """
    claims = get_jwt()
    if claims.get("role") != "ngo":
        return jsonify({"error": "Only NGOs can create events"}), 403

    user_id = get_jwt_identity()
    pk = int(user_id) if str(user_id).isdigit() else user_id
    ngo = db.session.get(NGO, pk)
    if not ngo:
        return jsonify({"error": "NGO not found"}), 404

    data = request.get_json(silent=True) or {}

    if not data.get("title"):
        return jsonify({"error": "Event title is required"}), 400
    if not data.get("event_date"):
        return jsonify({"error": "Event date is required"}), 400

    try:
        event_date = date.fromisoformat(data["event_date"])
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Parse start_time
    start_time = None
    if data.get("start_time"):
        from datetime import time as dtime
        try:
            parts = data["start_time"].split(":")
            start_time = dtime(int(parts[0]), int(parts[1]))
        except (ValueError, IndexError):
            pass

    event = Event(
        ngo_id=ngo.id,
        title=data["title"].strip(),
        description=data.get("description"),
        category=data.get("category"),
        city=data.get("city"),
        venue=data.get("venue"),
        event_date=event_date,
        start_time=start_time,
        duration_hours=float(data.get("duration_hours", 0.0) or 0.0),
        max_volunteers=int(data["max_volunteers"]) if data.get("max_volunteers") else None,
        image_url=data.get("image_url"),
        status="active",
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({"message": "Event created successfully!", "event": event.to_dict()}), 201


@events_bp.route("/<int:event_id>", methods=["PUT"])
@jwt_required()
def update_event(event_id):
    """Update an event. Only the owning NGO can update."""
    claims = get_jwt()
    if claims.get("role") != "ngo":
        return jsonify({"error": "Only NGOs can update events"}), 403

    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    if str(event.ngo_id) != str(get_jwt_identity()):
        return jsonify({"error": "You can only update your own events"}), 403

    data = request.get_json(silent=True) or {}

    for field in ["title", "description", "category", "city", "venue", "image_url", "status"]:
        if field in data:
            setattr(event, field, data[field])

    if "event_date" in data:
        try:
            event.event_date = date.fromisoformat(data["event_date"])
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    if "start_time" in data and data["start_time"]:
        from datetime import time as dtime
        try:
            parts = data["start_time"].split(":")
            event.start_time = dtime(int(parts[0]), int(parts[1]))
        except (ValueError, IndexError):
            pass

    if "duration_hours" in data:
        event.duration_hours = float(data["duration_hours"] or 0.0)
    if "max_volunteers" in data:
        event.max_volunteers = int(data["max_volunteers"]) if data["max_volunteers"] else None

    db.session.commit()
    return jsonify({"message": "Event updated!", "event": event.to_dict()}), 200


@events_bp.route("/<int:event_id>", methods=["DELETE"])
@jwt_required()
def delete_event(event_id):
    """Delete (cancel) an event. Only the owning NGO can do this."""
    claims = get_jwt()
    if claims.get("role") != "ngo":
        return jsonify({"error": "Only NGOs can delete events"}), 403

    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    if str(event.ngo_id) != str(get_jwt_identity()):
        return jsonify({"error": "You can only delete your own events"}), 403

    # Soft delete — mark as cancelled
    event.status = "cancelled"
    db.session.commit()
    return jsonify({"message": "Event cancelled successfully"}), 200


# ---------------------------------------------------------------------------
# Volunteer: Enroll / Un-enroll
# ---------------------------------------------------------------------------

@events_bp.route("/<int:event_id>/enroll", methods=["POST"])
@jwt_required()
def enroll_in_event(event_id):
    """Enroll the authenticated volunteer in an event."""
    claims = get_jwt()
    if claims.get("role") != "volunteer":
        return jsonify({"error": "Only volunteers can enroll in events"}), 403

    user_id = get_jwt_identity()
    pk = int(user_id) if str(user_id).isdigit() else user_id
    volunteer = db.session.get(Volunteer, pk)
    if not volunteer:
        return jsonify({"error": "Volunteer not found"}), 404

    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    if event.status != "active":
        return jsonify({"error": "This event is no longer accepting enrollments"}), 400

    if event.event_date < date.today():
        return jsonify({"error": "Cannot enroll in a past event"}), 400

    # Check spots
    if event.max_volunteers and event.enrolled_count() >= event.max_volunteers:
        return jsonify({"error": "This event is full. No spots remaining."}), 400

    # Check already enrolled
    existing = Enrollment.query.filter_by(volunteer_id=volunteer.id, event_id=event.id).first()
    if existing:
        return jsonify({"error": "You are already enrolled in this event"}), 409

    enrollment = Enrollment(volunteer_id=volunteer.id, event_id=event.id)

    try:
        db.session.add(enrollment)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Already enrolled"}), 409

    return jsonify({
        "message": f"Successfully enrolled in '{event.title}'!",
        "enrollment": enrollment.to_dict(),
        "event": event.to_dict(),
    }), 201


@events_bp.route("/<int:event_id>/enroll", methods=["DELETE"])
@jwt_required()
def unenroll_from_event(event_id):
    """Un-enroll the authenticated volunteer from an event."""
    claims = get_jwt()
    if claims.get("role") != "volunteer":
        return jsonify({"error": "Only volunteers can un-enroll from events"}), 403

    user_id = get_jwt_identity()
    pk = int(user_id) if str(user_id).isdigit() else user_id
    volunteer = db.session.get(Volunteer, pk)
    if not volunteer:
        return jsonify({"error": "Volunteer not found"}), 404

    enrollment = Enrollment.query.filter_by(
        volunteer_id=volunteer.id, event_id=event_id
    ).first()

    if not enrollment:
        return jsonify({"error": "You are not enrolled in this event"}), 404

    if enrollment.attended:
        return jsonify({"error": "Cannot un-enroll from an event you have already attended"}), 400

    db.session.delete(enrollment)
    db.session.commit()
    return jsonify({"message": "Successfully un-enrolled from the event"}), 200


# ---------------------------------------------------------------------------
# NGO: Manage Event Enrollments & Record Attendance
# ---------------------------------------------------------------------------

@events_bp.route("/<int:event_id>/enrollments", methods=["GET"])
@jwt_required()
def get_event_enrollments(event_id):
    """Get list of volunteers enrolled in this event. NGO owner only."""
    claims = get_jwt()
    if claims.get("role") != "ngo":
        return jsonify({"error": "Only NGOs can view event enrollments"}), 403

    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    if str(event.ngo_id) != str(get_jwt_identity()):
        return jsonify({"error": "You can only view enrollments for your own events"}), 403

    enrollments = event.enrollments.all()
    results = []
    for enr in enrollments:
        v = enr.volunteer
        results.append({
            "id": enr.id,
            "volunteer_id": enr.volunteer_id,
            "volunteer_name": v.name if v else "Unknown",
            "volunteer_email": v.email if v else "",
            "volunteer_phone": v.phone if v else "",
            "volunteer_city": v.city if v else "",
            "enrolled_at": enr.enrolled_at.isoformat() if enr.enrolled_at else None,
            "attended": enr.attended,
            "hours_logged": enr.hours_logged,
            "certificate_issued": enr.certificate_issued,
            "certificate_url": enr.certificate_url,
        })

    return jsonify({"event_id": event.id, "enrollments": results, "total": len(results)}), 200


@events_bp.route("/<int:event_id>/attendance", methods=["POST"])
@jwt_required()
def record_event_attendance(event_id):
    """Mark volunteer attendance and hours. NGO owner only.

    Body (JSON):
        enrollment_id*, attended (bool, default True), hours_logged (float), certificate_issued (bool)
    """
    claims = get_jwt()
    if claims.get("role") != "ngo":
        return jsonify({"error": "Only NGOs can record attendance"}), 403

    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    if str(event.ngo_id) != str(get_jwt_identity()):
        return jsonify({"error": "You can only record attendance for your own events"}), 403

    data = request.get_json(silent=True) or {}
    enrollment_id = data.get("enrollment_id")
    if not enrollment_id:
        return jsonify({"error": "enrollment_id is required"}), 400

    enr = Enrollment.query.filter_by(id=enrollment_id, event_id=event.id).first()
    if not enr:
        return jsonify({"error": "Enrollment record not found for this event"}), 404

    enr.attended = bool(data.get("attended", True))
    enr.hours_logged = float(data.get("hours_logged", event.duration_hours or 0.0) or 0.0)
    if data.get("certificate_issued", True):
        enr.certificate_issued = True
        enr.certificate_url = data.get("certificate_url", f"/certificates/cert_{enr.id}.pdf")

    # Update volunteer total hours
    v = enr.volunteer
    if v:
        all_attended = v.enrollments.filter_by(attended=True).all()
        v.total_hours = sum(e.hours_logged for e in all_attended if e.hours_logged)

    db.session.commit()
    return jsonify({
        "message": "Attendance and volunteer hours recorded successfully!",
        "enrollment": enr.to_dict()
    }), 200


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

@events_bp.route("/<int:event_id>/feedback", methods=["GET"])
def get_event_feedback(event_id):
    """Get all feedback for an event (public)."""
    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    feedbacks = event.feedback.order_by(Feedback.created_at.desc()).all()
    return jsonify({
        "event_id": event_id,
        "avg_rating": event.avg_rating(),
        "total_reviews": len(feedbacks),
        "feedback": [f.to_dict() for f in feedbacks],
    }), 200


@events_bp.route("/<int:event_id>/feedback", methods=["POST"])
@jwt_required()
def submit_feedback(event_id):
    """Submit feedback for an event the volunteer attended.

    Body (JSON):
        rating* (1-5), review_text?
    """
    claims = get_jwt()
    if claims.get("role") != "volunteer":
        return jsonify({"error": "Only volunteers can submit feedback"}), 403

    user_id = get_jwt_identity()
    pk = int(user_id) if str(user_id).isdigit() else user_id
    volunteer = db.session.get(Volunteer, pk)
    if not volunteer:
        return jsonify({"error": "Volunteer not found"}), 404

    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    # Must have attended
    enrollment = Enrollment.query.filter_by(
        volunteer_id=volunteer.id, event_id=event.id, attended=True
    ).first()
    if not enrollment:
        return jsonify({"error": "You can only leave feedback for events you have attended"}), 403

    # Duplicate check
    existing = Feedback.query.filter_by(volunteer_id=volunteer.id, event_id=event.id).first()
    if existing:
        return jsonify({"error": "You have already submitted feedback for this event"}), 409

    data = request.get_json(silent=True) or {}
    rating = data.get("rating")

    if rating is None or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400

    feedback = Feedback(
        volunteer_id=volunteer.id,
        event_id=event.id,
        rating=rating,
        review_text=data.get("review_text"),
    )

    try:
        db.session.add(feedback)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Feedback already submitted"}), 409

    return jsonify({
        "message": "Thank you for your feedback!",
        "feedback": feedback.to_dict(),
    }), 201
