"""Event validation schemas."""

from marshmallow import Schema, fields, validate


class EventCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    event_date = fields.Date(required=True)
    category = fields.Str(load_default=None, validate=validate.Length(max=100))
    city = fields.Str(load_default=None, validate=validate.Length(max=100))
    venue = fields.Str(load_default=None, validate=validate.Length(max=300))
    description = fields.Str(load_default=None)
    start_time = fields.Str(load_default=None)
    duration_hours = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    max_volunteers = fields.Int(load_default=None, validate=validate.Range(min=1))
    image_url = fields.Str(load_default=None, validate=validate.Length(max=500))


class EventUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=3, max=200))
    event_date = fields.Date()
    category = fields.Str(validate=validate.Length(max=100))
    city = fields.Str(validate=validate.Length(max=100))
    venue = fields.Str(validate=validate.Length(max=300))
    description = fields.Str()
    start_time = fields.Str()
    duration_hours = fields.Float(validate=validate.Range(min=0))
    max_volunteers = fields.Int(validate=validate.Range(min=1))
    image_url = fields.Str(validate=validate.Length(max=500))
    status = fields.Str(validate=validate.OneOf(["active", "completed", "cancelled"]))
