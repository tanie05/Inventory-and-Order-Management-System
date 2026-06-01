from flask import jsonify, request
from . import orders_bp
from .models import Order, OrderItem
from app.extensions import db
from app.products.models import Product
from app.customers.models import Customer


@orders_bp.route("/", methods=["GET"])
def get_orders():
    orders = Order.query.all()
    return jsonify([o.to_dict() for o in orders]), 200


@orders_bp.route("/<int:id>", methods=["GET"])
def get_order(id):
    order = Order.query.get(id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order.to_dict()), 200


@orders_bp.route("/", methods=["POST"])
def create_order():
    data = request.get_json()

    if not data.get("customer_id") or not data.get("items"):
        return jsonify({"error": "customer_id and items are required"}), 400

    customer = Customer.query.get(data["customer_id"])
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    total_amount = 0
    order_items = []

    for item in data["items"]:
        if not item.get("product_id") or not item.get("quantity"):
            return jsonify({"error": "Each item needs product_id and quantity"}), 400

        if item["quantity"] <= 0:
            return jsonify({"error": "Quantity must be greater than 0"}), 400

        product = Product.query.with_for_update().get(item["product_id"])
        if not product:
            return jsonify({"error": f"Product {item['product_id']} not found"}), 404

        if product.stock_quantity < item["quantity"]:
            return jsonify({"error": f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"}), 400

        product.stock_quantity -= item["quantity"]
        total_amount += float(product.price) * item["quantity"]

        order_items.append(OrderItem(
            product_id=product.id,
            quantity=item["quantity"],
            unit_price=product.price,
        ))

    order = Order(
        customer_id=data["customer_id"],
        total_amount=round(total_amount, 2),
        status="pending",
    )
    db.session.add(order)
    db.session.flush()

    for item in order_items:
        item.order_id = order.id
        db.session.add(item)

    db.session.commit()
    return jsonify(order.to_dict()), 201


@orders_bp.route("/<int:id>", methods=["DELETE"])
def delete_order(id):
    order = Order.query.get(id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    for item in order.items:
        product = Product.query.get(item.product_id)
        if product:
            product.stock_quantity += item.quantity

    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": f"Order {id} cancelled and stock restored"}), 200
