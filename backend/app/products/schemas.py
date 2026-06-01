from marshmallow import Schema, fields, validate, validates, ValidationError


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    sku = fields.Str(required=True, validate=validate.Length(min=1, max=60))
    description = fields.Str(load_default=None)
    price = fields.Float(required=True)
    stock_quantity = fields.Int(load_default=0)
    created_at = fields.DateTime(dump_only=True)

    @validates("price")
    def validate_price(self, value):
        if value < 0:
            raise ValidationError("price cannot be negative")

    @validates("stock_quantity")
    def validate_stock(self, value):
        if value < 0:
            raise ValidationError("stock_quantity cannot be negative")


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
product_update_schema = ProductSchema(partial=True)
