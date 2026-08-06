from datetime import datetime, timezone
from ..extensions import db


class Enrollment(db.Model):
    """A volunteer's enrollment into an event."""

    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey("volunteers.id"), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False, index=True)

    enrolled_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    attended = db.Column(db.Boolean, default=False)
    hours_logged = db.Column(db.Float, default=0.0)
    certificate_issued = db.Column(db.Boolean, default=False)
    certificate_url = db.Column(db.String(500), nullable=True)

    # Unique constraint — one volunteer per event
    __table_args__ = (
        db.UniqueConstraint("volunteer_id", "event_id", name="uq_volunteer_event"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "volunteer_id": self.volunteer_id,
            "event_id": self.event_id,
            "enrolled_at": self.enrolled_at.isoformat() if self.enrolled_at else None,
            "attended": self.attended,
            "hours_logged": self.hours_logged,
            "certificate_issued": self.certificate_issued,
            "certificate_url": self.certificate_url,
        }

    def __repr__(self):
        return f"<Enrollment volunteer={self.volunteer_id} event={self.event_id}>"
