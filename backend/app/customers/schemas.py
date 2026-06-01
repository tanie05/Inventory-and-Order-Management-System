from marshmallow import Schema, fields, validate


class CustomerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True)
    phone = fields.Str(load_default=None, validate=validate.Length(max=30))
    created_at = fields.DateTime(dump_only=True)


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
