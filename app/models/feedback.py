from datetime import datetime, timezone
from ..extensions import db


class Feedback(db.Model):
    """Post-event feedback submitted by a volunteer."""

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey("volunteers.id"), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False, index=True)

    rating = db.Column(db.Integer, nullable=False)       # 1-5 stars
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # One feedback per volunteer per event
    __table_args__ = (
        db.UniqueConstraint("volunteer_id", "event_id", name="uq_volunteer_event_feedback"),
        db.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_rating_range"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "volunteer_id": self.volunteer_id,
            "event_id": self.event_id,
            "rating": self.rating,
            "review_text": self.review_text,
            "volunteer_name": self.volunteer.name if self.volunteer else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Feedback volunteer={self.volunteer_id} event={self.event_id} rating={self.rating}>"
