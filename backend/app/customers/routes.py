from flask import jsonify, request
from . import customers_bp
from .models import Customer
from app.extensions import db


@customers_bp.route("/", methods=["GET"])
def get_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers]), 200


@customers_bp.route("/<int:id>", methods=["GET"])
def get_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(customer.to_dict()), 200


@customers_bp.route("/", methods=["POST"])
def create_customer():
    data = request.get_json()

    if not data.get("name") or not data.get("email"):
        return jsonify({"error": "name and email are required"}), 400

    if Customer.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    customer = Customer(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.to_dict()), 201


@customers_bp.route("/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {id} deleted"}), 200
