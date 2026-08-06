"""Authentication routes — register and login for both volunteers and NGOs."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

from ..extensions import db, bcrypt
from ..models.volunteer import Volunteer
from ..models.ngo import NGO

auth_bp = Blueprint("auth", __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_required(data: dict, fields: list[str]):
    """Return list of missing required fields."""
    return [f for f in fields if not data.get(f)]


# ---------------------------------------------------------------------------
# Volunteer Auth
# ---------------------------------------------------------------------------

@auth_bp.route("/volunteer/register", methods=["POST"])
@auth_bp.route("/volunteers", methods=["POST"])
def volunteer_register():
    """Register a new volunteer.

    Body (JSON):
        name, email, password, phone?, city?, interests?, availability?
    """
    data = request.get_json(silent=True) or {}

    missing = _validate_required(data, ["name", "email", "password"])
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    # Check duplicate email
    if Volunteer.query.filter_by(email=data["email"].lower().strip()).first():
        return jsonify({"error": "A volunteer account with this email already exists"}), 409

    password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    volunteer = Volunteer(
        name=data["name"].strip(),
        email=data["email"].lower().strip(),
        password_hash=password_hash,
        phone=data.get("phone"),
        city=data.get("city"),
        bio=data.get("bio"),
        interests=",".join(data["interests"]) if isinstance(data.get("interests"), list) else data.get("interests", ""),
        availability=data.get("availability"),
    )

    try:
        db.session.add(volunteer)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already in use"}), 409

    token = create_access_token(identity=str(volunteer.id), additional_claims={"role": "volunteer"})

    return jsonify({
        "message": "Volunteer registered successfully!",
        "access_token": token,
        "volunteer": volunteer.to_dict(include_private=True),
    }), 201


@auth_bp.route("/volunteer/login", methods=["POST"])
def volunteer_login():
    """Login a volunteer.

    Body (JSON):
        email, password
    """
    data = request.get_json(silent=True) or {}

    missing = _validate_required(data, ["email", "password"])
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    volunteer = Volunteer.query.filter_by(email=data["email"].lower().strip()).first()

    if not volunteer or not bcrypt.check_password_hash(volunteer.password_hash, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    if not volunteer.is_active:
        return jsonify({"error": "Account is deactivated. Please contact support."}), 403

    token = create_access_token(identity=str(volunteer.id), additional_claims={"role": "volunteer"})

    return jsonify({
        "message": "Login successful!",
        "access_token": token,
        "volunteer": volunteer.to_dict(include_private=True),
    }), 200


# ---------------------------------------------------------------------------
# NGO Auth
# ---------------------------------------------------------------------------

@auth_bp.route("/ngo/register", methods=["POST"])
@auth_bp.route("/ngos", methods=["POST"])
def ngo_register():
    """Register a new NGO.

    Body (JSON):
        name, email, password, registration_number?, phone?, city?, state?, description?, cause_areas?
    """
    data = request.get_json(silent=True) or {}

    missing = _validate_required(data, ["name", "email", "password"])
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    if NGO.query.filter_by(email=data["email"].lower().strip()).first():
        return jsonify({"error": "An NGO with this email already exists"}), 409

    password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    ngo = NGO(
        name=data["name"].strip(),
        email=data["email"].lower().strip(),
        password_hash=password_hash,
        registration_number=data.get("registration_number"),
        phone=data.get("phone"),
        city=data.get("city"),
        state=data.get("state"),
        address=data.get("address"),
        website=data.get("website"),
        description=data.get("description"),
        cause_areas=",".join(data["cause_areas"]) if isinstance(data.get("cause_areas"), list) else data.get("cause_areas", ""),
    )

    try:
        db.session.add(ngo)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email or registration number already in use"}), 409

    token = create_access_token(identity=str(ngo.id), additional_claims={"role": "ngo"})

    return jsonify({
        "message": "NGO registered successfully! Your account will be reviewed and verified shortly.",
        "access_token": token,
        "ngo": ngo.to_dict(include_private=True),
    }), 201


@auth_bp.route("/ngo/login", methods=["POST"])
def ngo_login():
    """Login an NGO.

    Body (JSON):
        email, password
    """
    data = request.get_json(silent=True) or {}

    missing = _validate_required(data, ["email", "password"])
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    ngo = NGO.query.filter_by(email=data["email"].lower().strip()).first()

    if not ngo or not bcrypt.check_password_hash(ngo.password_hash, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    if not ngo.is_active:
        return jsonify({"error": "Account is deactivated. Please contact support."}), 403

    token = create_access_token(identity=str(ngo.id), additional_claims={"role": "ngo"})

    return jsonify({
        "message": "Login successful!",
        "access_token": token,
        "ngo": ngo.to_dict(include_private=True),
    }), 200
