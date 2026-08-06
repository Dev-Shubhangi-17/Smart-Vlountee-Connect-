from datetime import datetime, timezone
from ..extensions import db


class Volunteer(db.Model):
    """Registered volunteer user."""

    __tablename__ = "volunteers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    # Interests stored as comma-separated string e.g. "Education,Healthcare,Environment"
    interests = db.Column(db.Text, nullable=True, default="")

    # Availability e.g. "Weekends", "Weekdays", "Anytime"
    availability = db.Column(db.String(100), nullable=True)

    profile_picture = db.Column(db.String(500), nullable=True)
    total_hours = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    enrollments = db.relationship("Enrollment", backref="volunteer", lazy="dynamic", cascade="all, delete-orphan")
    feedback = db.relationship("Feedback", backref="volunteer", lazy="dynamic", cascade="all, delete-orphan")

    def interests_list(self):
        """Return interests as a Python list."""
        if not self.interests:
            return []
        return [i.strip() for i in self.interests.split(",") if i.strip()]

    def to_dict(self, include_private=False):
        data = {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "bio": self.bio,
            "interests": self.interests_list(),
            "availability": self.availability,
            "profile_picture": self.profile_picture,
            "total_hours": self.total_hours,
            "events_attended": self.enrollments.filter_by(attended=True).count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_private:
            data["email"] = self.email
            data["phone"] = self.phone
        return data

    def __repr__(self):
        return f"<Volunteer {self.email}>"
