"""Contact form routes — store messages in DB and optionally send email."""

from flask import Blueprint, request, jsonify
from ..extensions import db, mail
from ..models.contact import ContactMessage

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("", methods=["POST"])
def submit_contact():
    """Handle a contact form submission.

    Body (JSON):
        name*, email*, message*, subject?
    """
    data = request.get_json(silent=True) or {}

    missing = [f for f in ["name", "email", "message"] if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # Basic email validation
    if "@" not in data["email"] or "." not in data["email"]:
        return jsonify({"error": "Please provide a valid email address"}), 400

    msg = ContactMessage(
        name=data["name"].strip(),
        email=data["email"].lower().strip(),
        subject=data.get("subject", "General Enquiry"),
        message=data["message"].strip(),
    )

    db.session.add(msg)
    db.session.commit()

    # Optional: send email notification (silently fails if mail not configured)
    try:
        from flask_mail import Message as MailMessage
        from flask import current_app
        if current_app.config.get("MAIL_USERNAME"):
            email_msg = MailMessage(
                subject=f"[Smart Volunteer Connect] New Message: {msg.subject}",
                recipients=[current_app.config["MAIL_DEFAULT_SENDER"]],
                body=(
                    f"New contact message from {msg.name} ({msg.email})\n\n"
                    f"Subject: {msg.subject}\n\n"
                    f"Message:\n{msg.message}"
                ),
            )
            mail.send(email_msg)
    except Exception:
        pass  # Email sending is optional — DB save already succeeded

    return jsonify({
        "message": "Thank you for reaching out! We'll get back to you within 24 hours.",
        "contact_id": msg.id,
    }), 201
