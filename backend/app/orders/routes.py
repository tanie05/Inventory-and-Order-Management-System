from flask import jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from . import orders_bp
from .models import Order, OrderItem
from .schemas import order_schema, orders_schema, order_create_schema
from app.extensions import db
from app.products.models import Product
from app.customers.models import Customer
from app.logger import setup_logger

logger = setup_logger(__name__)


@orders_bp.route("/", methods=["GET"])
@jwt_required()
def get_orders():
    try:
        logger.debug("Fetching all orders")
        orders = Order.query.all()
        logger.debug(f"Returned {len(orders)} orders")
        return jsonify(orders_schema.dump(orders)), 200
    except Exception as e:
        logger.error(f"Failed to fetch orders: {e}")
        return jsonify({"error": "Failed to fetch orders", "details": str(e)}), 500


@orders_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_order(id):
    try:
        logger.debug(f"Fetching order id={id}")
        order = Order.query.get(id)
        if not order:
            logger.warning(f"Order id={id} not found")
            return jsonify({"error": f"Order with id {id} not found"}), 404
        return jsonify(order_schema.dump(order)), 200
    except Exception as e:
        logger.error(f"Failed to fetch order id={id}: {e}")
        return jsonify({"error": "Failed to fetch order", "details": str(e)}), 500


@orders_bp.route("/", methods=["POST"])
@jwt_required()
def create_order():
    try:
        data = request.get_json()
        if not data:
            logger.warning("Create order called with empty body")
            return jsonify({"error": "Request body must be JSON"}), 400

        validated = order_create_schema.load(data)
        logger.debug(f"Creating order for customer_id={validated['customer_id']}")

        customer = Customer.query.get(validated["customer_id"])
        if not customer:
            logger.warning(f"Order creation failed - customer id={validated['customer_id']} not found")
            return jsonify({"error": f"Customer with id {validated['customer_id']} not found"}), 404

        total_amount = 0
        order_items = []

        for item in validated["items"]:
            product = Product.query.with_for_update().get(item["product_id"])
            if not product:
                logger.warning(f"Order creation failed - product id={item['product_id']} not found")
                return jsonify({"error": f"Product with id {item['product_id']} not found"}), 404

            if product.stock_quantity < item["quantity"]:
                logger.warning(f"Insufficient stock for product id={product.id} - requested={item['quantity']} available={product.stock_quantity}")
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
        logger.debug(f"Order created: id={order.id} total={order.total_amount}")
        return jsonify(order_schema.dump(order)), 201

    except ValidationError as e:
        logger.warning(f"Order validation failed: {e.messages}")
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create order: {e}")
        return jsonify({"error": "Failed to create order", "details": str(e)}), 500


@orders_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_order(id):
    try:
        order = Order.query.get(id)
        if not order:
            logger.warning(f"Cancel attempted on non-existent order id={id}")
            return jsonify({"error": f"Order with id {id} not found"}), 404

        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock_quantity += item.quantity
                logger.debug(f"Restored {item.quantity} units to product id={product.id}")

        db.session.delete(order)
        db.session.commit()
        logger.debug(f"Order cancelled: id={id}")
        return jsonify({"message": f"Order {id} cancelled and stock restored"}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to cancel order id={id}: {e}")
        return jsonify({"error": "Failed to cancel order", "details": str(e)}), 500
