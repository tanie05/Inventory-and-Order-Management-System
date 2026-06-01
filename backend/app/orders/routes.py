from flask import jsonify
from . import orders_bp
from .models import Order


@orders_bp.route("/", methods=["GET"])
def get_orders():
    orders = Order.query.all()
    return jsonify([o.to_dict() for o in orders]), 200
