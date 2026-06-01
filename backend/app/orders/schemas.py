from marshmallow import Schema, fields, validate, validates, ValidationError


class OrderItemInputSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True)

    @validates("quantity")
    def validate_quantity(self, value):
        if value <= 0:
            raise ValidationError("quantity must be greater than 0")


class OrderItemSchema(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int(dump_only=True)
    product_name = fields.Str(dump_only=True)
    quantity = fields.Int(dump_only=True)
    unit_price = fields.Float(dump_only=True)
    subtotal = fields.Float(dump_only=True)


class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    customer_id = fields.Int(required=True)
    customer_name = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    total_amount = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    items = fields.List(fields.Nested(OrderItemSchema), dump_only=True)


class OrderCreateSchema(Schema):
    customer_id = fields.Int(required=True)
    items = fields.List(fields.Nested(OrderItemInputSchema), required=True, validate=validate.Length(min=1))


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
order_create_schema = OrderCreateSchema()
