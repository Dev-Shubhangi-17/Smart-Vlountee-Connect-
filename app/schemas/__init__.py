"""Schemas package."""

from .auth_schema import VolunteerRegisterSchema, NGORegisterSchema, LoginSchema
from .event_schema import EventCreateSchema, EventUpdateSchema
from .volunteer_schema import VolunteerUpdateSchema
from .ngo_schema import NGOUpdateSchema

__all__ = [
    "VolunteerRegisterSchema",
    "NGORegisterSchema",
    "LoginSchema",
    "EventCreateSchema",
    "EventUpdateSchema",
    "VolunteerUpdateSchema",
    "NGOUpdateSchema",
]
