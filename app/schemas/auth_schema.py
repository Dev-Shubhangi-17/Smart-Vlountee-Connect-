"""Authentication validation schemas."""

from marshmallow import Schema, fields, validate


class VolunteerRegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True, validate=validate.Length(max=200))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    phone = fields.Str(load_default=None, validate=validate.Length(max=20))
    city = fields.Str(load_default=None, validate=validate.Length(max=100))
    bio = fields.Str(load_default=None)
    interests = fields.Raw(load_default=[])
    availability = fields.Str(load_default=None, validate=validate.Length(max=100))


class NGORegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    email = fields.Email(required=True, validate=validate.Length(max=200))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    registration_number = fields.Str(load_default=None, validate=validate.Length(max=100))
    phone = fields.Str(load_default=None, validate=validate.Length(max=20))
    city = fields.Str(load_default=None, validate=validate.Length(max=100))
    state = fields.Str(load_default=None, validate=validate.Length(max=100))
    address = fields.Str(load_default=None)
    website = fields.Str(load_default=None, validate=validate.Length(max=300))
    description = fields.Str(load_default=None)
    cause_areas = fields.Raw(load_default=[])


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
