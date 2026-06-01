from flask import jsonify, request
from marshmallow import ValidationError
from . import orders_bp
from .models import Order, OrderItem
from .schemas import order_schema, orders_schema, order_create_schema
from app.extensions import db
from app.products.models import Product
from app.customers.models import Customer


@orders_bp.route("/", methods=["GET"])
def get_orders():
    try:
        orders = Order.query.all()
        return jsonify(orders_schema.dump(orders)), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch orders", "details": str(e)}), 500


@orders_bp.route("/<int:id>", methods=["GET"])
def get_order(id):
    try:
        order = Order.query.get(id)
        if not order:
            return jsonify({"error": f"Order with id {id} not found"}), 404
        return jsonify(order_schema.dump(order)), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch order", "details": str(e)}), 500


@orders_bp.route("/", methods=["POST"])
def create_order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        validated = order_create_schema.load(data)

        customer = Customer.query.get(validated["customer_id"])
        if not customer:
            return jsonify({"error": f"Customer with id {validated['customer_id']} not found"}), 404

        total_amount = 0
        order_items = []

        for item in validated["items"]:
            product = Product.query.with_for_update().get(item["product_id"])
            if not product:
                return jsonify({"error": f"Product with id {item['product_id']} not found"}), 404

            if product.stock_quantity < item["quantity"]:
                return jsonify({
                    "error": f"Insufficient stock for '{product.name}'. Available: {product.stock_quantity}"
                }), 400

            product.stock_quantity -= item["quantity"]
            total_amount += float(product.price) * item["quantity"]

            order_items.append(OrderItem(
                product_id=product.id,
                quantity=item["quantity"],
                unit_price=product.price,
            ))

        order = Order(
            customer_id=validated["customer_id"],
            total_amount=round(total_amount, 2),
            status="pending",
        )
        db.session.add(order)
        db.session.flush()

        for item in order_items:
            item.order_id = order.id
            db.session.add(item)

        db.session.commit()
        return jsonify(order_schema.dump(order)), 201

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create order", "details": str(e)}), 500


@orders_bp.route("/<int:id>", methods=["DELETE"])
def delete_order(id):
    try:
        order = Order.query.get(id)
        if not order:
            return jsonify({"error": f"Order with id {id} not found"}), 404

        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock_quantity += item.quantity

        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": f"Order {id} cancelled and stock restored"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to cancel order", "details": str(e)}), 500
