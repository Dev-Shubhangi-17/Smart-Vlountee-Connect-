from datetime import datetime, timezone
from ..extensions import db


class NGO(db.Model):
    """Registered NGO organization."""

    __tablename__ = "ngos"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    registration_number = db.Column(db.String(100), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(300), nullable=True)
    description = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(500), nullable=True)

    # Cause areas e.g. "Education,Healthcare,Environment,Animal Welfare"
    cause_areas = db.Column(db.Text, nullable=True, default="")

    # Whether the NGO has been verified by platform admins
    verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    events = db.relationship("Event", backref="ngo", lazy="dynamic", cascade="all, delete-orphan")

    def cause_areas_list(self):
        """Return cause areas as a Python list."""
        if not self.cause_areas:
            return []
        return [c.strip() for c in self.cause_areas.split(",") if c.strip()]

    def to_dict(self, include_private=False):
        data = {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "description": self.description,
            "logo_url": self.logo_url,
            "website": self.website,
            "cause_areas": self.cause_areas_list(),
            "verified": self.verified,
            "events_count": self.events.filter_by(status="active").count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_private:
            data["email"] = self.email
            data["phone"] = self.phone
            data["registration_number"] = self.registration_number
            data["address"] = self.address
        return data

    def __repr__(self):
        return f"<NGO {self.name}>"
