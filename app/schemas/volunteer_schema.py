"""Volunteer schemas."""

from marshmallow import Schema, fields, validate


class VolunteerUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2, max=120))
    phone = fields.Str(validate=validate.Length(max=20))
    city = fields.Str(validate=validate.Length(max=100))
    bio = fields.Str()
    interests = fields.Raw()
    availability = fields.Str(validate=validate.Length(max=100))
    profile_picture = fields.Str(validate=validate.Length(max=500))
