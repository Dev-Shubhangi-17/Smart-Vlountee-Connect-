"""Authentication routes — register, login, current-user retrieval, and logout."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import IntegrityError

from ..extensions import db, bcrypt
from ..models.volunteer import Volunteer
from ..models.ngo import NGO
from ..utils.security import validate_email_format, validate_password_strength

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
        name, email, password, phone?, city?, interests?, availability?, bio?
    """
    data = request.get_json(silent=True) or {}

    missing = _validate_required(data, ["name", "email", "password"])
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    if not validate_email_format(data["email"]):
        return jsonify({"error": "Invalid email address format"}), 400

    valid_pw, pw_err = validate_password_strength(data["password"])
    if not valid_pw:
        return jsonify({"error": pw_err}), 400

    # Check duplicate email
    email = data["email"].lower().strip()
    if Volunteer.query.filter_by(email=email).first():
        return jsonify({"error": "A volunteer account with this email already exists"}), 409

    password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    interests_val = data.get("interests", "")
    if isinstance(interests_val, list):
        interests_str = ",".join(str(i).strip() for i in interests_val if str(i).strip())
    else:
        interests_str = str(interests_val or "").strip()

    volunteer = Volunteer(
        name=data["name"].strip(),
        email=email,
        password_hash=password_hash,
        phone=data.get("phone"),
        city=data.get("city"),
        bio=data.get("bio"),
        interests=interests_str,
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
        "role": "volunteer",
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

    email = data["email"].lower().strip()
    volunteer = Volunteer.query.filter_by(email=email).first()

    if not volunteer or not bcrypt.check_password_hash(volunteer.password_hash, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    if not volunteer.is_active:
        return jsonify({"error": "Account is deactivated. Please contact support."}), 403

    token = create_access_token(identity=str(volunteer.id), additional_claims={"role": "volunteer"})

    return jsonify({
        "message": "Login successful!",
        "access_token": token,
        "role": "volunteer",
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

    if not validate_email_format(data["email"]):
        return jsonify({"error": "Invalid email address format"}), 400

    valid_pw, pw_err = validate_password_strength(data["password"])
    if not valid_pw:
        return jsonify({"error": pw_err}), 400

    email = data["email"].lower().strip()
    if NGO.query.filter_by(email=email).first():
        return jsonify({"error": "An NGO with this email already exists"}), 409

    reg_number = data.get("registration_number")
    if reg_number and NGO.query.filter_by(registration_number=reg_number.strip()).first():
        return jsonify({"error": "An NGO with this registration number already exists"}), 409

    password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    cause_val = data.get("cause_areas", "")
    if isinstance(cause_val, list):
        cause_str = ",".join(str(c).strip() for c in cause_val if str(c).strip())
    else:
        cause_str = str(cause_val or "").strip()

    ngo = NGO(
        name=data["name"].strip(),
        email=email,
        password_hash=password_hash,
        registration_number=reg_number.strip() if reg_number else None,
        phone=data.get("phone"),
        city=data.get("city"),
        state=data.get("state"),
        address=data.get("address"),
        website=data.get("website"),
        description=data.get("description"),
        cause_areas=cause_str,
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
        "role": "ngo",
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

    email = data["email"].lower().strip()
    ngo = NGO.query.filter_by(email=email).first()

    if not ngo or not bcrypt.check_password_hash(ngo.password_hash, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    if not ngo.is_active:
        return jsonify({"error": "Account is deactivated. Please contact support."}), 403

    token = create_access_token(identity=str(ngo.id), additional_claims={"role": "ngo"})

    return jsonify({
        "message": "Login successful!",
        "access_token": token,
        "role": "ngo",
        "ngo": ngo.to_dict(include_private=True),
    }), 200


# ---------------------------------------------------------------------------
# Current User Retrieval & Logout
# ---------------------------------------------------------------------------

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Retrieve the currently authenticated user's profile and role."""
    claims = get_jwt()
    user_id = get_jwt_identity()
    role = claims.get("role")

    pk = int(user_id) if str(user_id).isdigit() else user_id

    if role == "volunteer":
        user = db.session.get(Volunteer, pk)
        if not user:
            return jsonify({"error": "Volunteer not found"}), 404
        return jsonify({
            "role": "volunteer",
            "user": user.to_dict(include_private=True)
        }), 200
    elif role == "ngo":
        user = db.session.get(NGO, pk)
        if not user:
            return jsonify({"error": "NGO not found"}), 404
        return jsonify({
            "role": "ngo",
            "user": user.to_dict(include_private=True)
        }), 200
    else:
        return jsonify({"error": "Unknown user role"}), 400


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Client-side token invalidation confirmation."""
    return jsonify({"message": "Logged out successfully"}), 200
