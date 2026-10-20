"""Volunteer routes — profile, enrollments, certificates, stats, smart matching."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import date

from ..extensions import db
from ..models.volunteer import Volunteer
from ..models.event import Event
from ..models.enrollment import Enrollment

volunteers_bp = Blueprint("volunteers", __name__)

from .auth import volunteer_register

@volunteers_bp.route("", methods=["POST"])
def register_volunteer_alias():
    return volunteer_register()


def _get_current_volunteer():
    """Return the currently authenticated volunteer or raise 404."""
    claims = get_jwt()
    if claims.get("role") != "volunteer":
        return None, (jsonify({"error": "Access restricted to volunteers"}), 403)
    user_id = get_jwt_identity()
    pk = int(user_id) if str(user_id).isdigit() else user_id
    volunteer = db.session.get(Volunteer, pk)
    if not volunteer:
        return None, (jsonify({"error": "Volunteer not found"}), 404)
    return volunteer, None


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@volunteers_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    """Get the authenticated volunteer's profile."""
    volunteer, err = _get_current_volunteer()
    if err:
        return err
    return jsonify(volunteer.to_dict(include_private=True)), 200


@volunteers_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update the authenticated volunteer's profile.

    Body (JSON — all fields optional):
        name, phone, city, bio, interests, availability, profile_picture
    """
    volunteer, err = _get_current_volunteer()
    if err:
        return err

    data = request.get_json(silent=True) or {}

    if "name" in data:
        volunteer.name = data["name"].strip()
    if "phone" in data:
        volunteer.phone = data["phone"]
    if "city" in data:
        volunteer.city = data["city"]
    if "bio" in data:
        volunteer.bio = data["bio"]
    if "interests" in data:
        interests = data["interests"]
        volunteer.interests = ",".join(interests) if isinstance(interests, list) else str(interests or "")
    if "availability" in data:
        volunteer.availability = data["availability"]
    if "profile_picture" in data:
        volunteer.profile_picture = data["profile_picture"]

    db.session.commit()
    return jsonify({"message": "Profile updated!", "volunteer": volunteer.to_dict(include_private=True)}), 200


# ---------------------------------------------------------------------------
# My Enrollments
# ---------------------------------------------------------------------------

@volunteers_bp.route("/me/enrollments", methods=["GET"])
@jwt_required()
def get_my_enrollments():
    """List all events the volunteer is enrolled in."""
    volunteer, err = _get_current_volunteer()
    if err:
        return err

    filter_status = request.args.get("status")  # upcoming | past | attended
    today = date.today()

    enrollments = volunteer.enrollments.all()

    result = []
    for enr in enrollments:
        event = enr.event
        if not event:
            continue

        if filter_status == "upcoming" and event.event_date < today:
            continue
        if filter_status == "past" and event.event_date >= today:
            continue
        if filter_status == "attended" and not enr.attended:
            continue

        record = enr.to_dict()
        record["event"] = event.to_dict()
        result.append(record)

    return jsonify({"enrollments": result, "total": len(result)}), 200


# ---------------------------------------------------------------------------
# Certificates
# ---------------------------------------------------------------------------

@volunteers_bp.route("/me/certificates", methods=["GET"])
@jwt_required()
def get_my_certificates():
    """List all certificates earned by the volunteer."""
    volunteer, err = _get_current_volunteer()
    if err:
        return err

    certs = volunteer.enrollments.filter_by(certificate_issued=True).all()
    result = []
    for enr in certs:
        record = {
            "enrollment_id": enr.id,
            "event": enr.event.to_dict() if enr.event else None,
            "certificate_url": enr.certificate_url,
            "hours_logged": enr.hours_logged,
        }
        result.append(record)

    return jsonify({"certificates": result, "total": len(result)}), 200


# ---------------------------------------------------------------------------
# Stats / Dashboard
# ---------------------------------------------------------------------------

@volunteers_bp.route("/me/stats", methods=["GET"])
@jwt_required()
def get_my_stats():
    """Return volunteer dashboard statistics."""
    volunteer, err = _get_current_volunteer()
    if err:
        return err

    total_enrolled = volunteer.enrollments.count()
    total_attended = volunteer.enrollments.filter_by(attended=True).count()
    total_certificates = volunteer.enrollments.filter_by(certificate_issued=True).count()
    total_feedback_given = volunteer.feedback.count()

    # Recalculate total hours from enrollments
    all_enrollments = volunteer.enrollments.filter_by(attended=True).all()
    total_hours = sum(e.hours_logged for e in all_enrollments if e.hours_logged)

    return jsonify({
        "volunteer_id": volunteer.id,
        "name": volunteer.name,
        "total_enrolled": total_enrolled,
        "total_attended": total_attended,
        "total_hours": total_hours,
        "total_certificates": total_certificates,
        "total_feedback_given": total_feedback_given,
    }), 200


# ---------------------------------------------------------------------------
# Smart Matching
# ---------------------------------------------------------------------------

@volunteers_bp.route("/me/matches", methods=["GET"])
@jwt_required()
def get_smart_matches():
    """Return events matched to the volunteer based on interests and city."""
    volunteer, err = _get_current_volunteer()
    if err:
        return err

    today = date.today()
    interests = volunteer.interests_list()
    city = (volunteer.city or "").lower().strip()

    # Only active upcoming events the volunteer hasn't already enrolled in
    enrolled_event_ids = {enr.event_id for enr in volunteer.enrollments.all()}

    query = Event.query.filter(
        Event.event_date >= today,
        Event.status == "active"
    )
    if enrolled_event_ids:
        query = query.filter(Event.id.notin_(enrolled_event_ids))

    upcoming_events = query.all()

    scored = []
    for event in upcoming_events:
        score = 0
        if event.category and event.category in interests:
            score += 3
        if city and event.city and event.city.lower().strip() == city:
            score += 2
        if event.event_date >= today:
            score += 1
        scored.append((score, event))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_matches = [event.to_dict() for score, event in scored[:10]]

    return jsonify({"matches": top_matches, "total": len(top_matches)}), 200


# ---------------------------------------------------------------------------
# Admin / Demo: Mark attendance & issue certificate
# ---------------------------------------------------------------------------

@volunteers_bp.route("/me/enrollments/<int:enrollment_id>/attend", methods=["POST"])
@jwt_required()
def mark_attended(enrollment_id):
    """Mark an enrollment as attended and log hours."""
    volunteer, err = _get_current_volunteer()
    if err:
        return err

    enr = db.session.get(Enrollment, enrollment_id)
    if not enr:
        return jsonify({"error": "Enrollment not found"}), 404

    if enr.volunteer_id != volunteer.id:
        return jsonify({"error": "Not authorized"}), 403

    data = request.get_json(silent=True) or {}
    enr.attended = True
    enr.hours_logged = data.get("hours_logged", enr.event.duration_hours if enr.event else 0)
    enr.certificate_issued = True
    enr.certificate_url = data.get("certificate_url", f"/certificates/cert_{enr.id}.pdf")

    all_attended = volunteer.enrollments.filter_by(attended=True).all()
    volunteer.total_hours = sum(e.hours_logged for e in all_attended if e.hours_logged)

    db.session.commit()
    return jsonify({"message": "Attendance marked and certificate issued!", "enrollment": enr.to_dict()}), 200
