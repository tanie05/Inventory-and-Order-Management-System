from flask import jsonify
from . import customers_bp
from .models import Customer


@customers_bp.route("/", methods=["GET"])
def get_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers]), 200
