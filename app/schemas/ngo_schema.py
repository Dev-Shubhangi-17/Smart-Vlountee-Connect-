"""NGO schemas."""

from marshmallow import Schema, fields, validate


class NGOUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2, max=200))
    phone = fields.Str(validate=validate.Length(max=20))
    city = fields.Str(validate=validate.Length(max=100))
    state = fields.Str(validate=validate.Length(max=100))
    address = fields.Str()
    website = fields.Str(validate=validate.Length(max=300))
    description = fields.Str()
    cause_areas = fields.Raw()
    logo_url = fields.Str(validate=validate.Length(max=500))
