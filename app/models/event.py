from datetime import datetime, timezone
from ..extensions import db


class Event(db.Model):
    """Volunteer event posted by an NGO."""

    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    ngo_id = db.Column(db.Integer, db.ForeignKey("ngos.id"), nullable=False, index=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)   # Education, Healthcare, Environment, etc.
    city = db.Column(db.String(100), nullable=True, index=True)
    venue = db.Column(db.String(300), nullable=True)

    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    duration_hours = db.Column(db.Float, nullable=True, default=0.0)  # How many hours it lasts

    max_volunteers = db.Column(db.Integer, nullable=True)  # None = unlimited
    image_url = db.Column(db.String(500), nullable=True)

    # Status: active | cancelled | completed
    status = db.Column(db.String(20), default="active", nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    enrollments = db.relationship("Enrollment", backref="event", lazy="dynamic", cascade="all, delete-orphan")
    feedback = db.relationship("Feedback", backref="event", lazy="dynamic", cascade="all, delete-orphan")

    def enrolled_count(self):
        return self.enrollments.count()

    def avg_rating(self):
        """Average feedback rating for this event."""
        feedbacks = self.feedback.all()
        if not feedbacks:
            return None
        return round(sum(f.rating for f in feedbacks) / len(feedbacks), 1)

    def spots_left(self):
        if self.max_volunteers is None:
            return None  # unlimited
        return max(0, self.max_volunteers - self.enrolled_count())

    def to_dict(self, include_ngo=True):
        data = {
            "id": self.id,
            "ngo_id": self.ngo_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "city": self.city,
            "venue": self.venue,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "start_time": self.start_time.strftime("%H:%M") if self.start_time else None,
            "duration_hours": self.duration_hours,
            "max_volunteers": self.max_volunteers,
            "enrolled_count": self.enrolled_count(),
            "spots_left": self.spots_left(),
            "avg_rating": self.avg_rating(),
            "image_url": self.image_url,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_ngo and self.ngo:
            data["ngo"] = {"id": self.ngo.id, "name": self.ngo.name, "logo_url": self.ngo.logo_url}
        return data

    def __repr__(self):
        return f"<Event {self.title}>"
