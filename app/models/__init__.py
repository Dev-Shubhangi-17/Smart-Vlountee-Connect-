"""Models package — import all models here so Flask-Migrate can detect them."""

from .volunteer import Volunteer
from .ngo import NGO
from .event import Event
from .enrollment import Enrollment
from .feedback import Feedback
from .contact import ContactMessage

__all__ = [
    "Volunteer",
    "NGO",
    "Event",
    "Enrollment",
    "Feedback",
    "ContactMessage",
]
