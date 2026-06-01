from flask import jsonify, request
from marshmallow import ValidationError
from . import customers_bp
from .models import Customer
from .schemas import customer_schema, customers_schema
from app.extensions import db


@customers_bp.route("/", methods=["GET"])
def get_customers():
    try:
        customers = Customer.query.all()
        return jsonify(customers_schema.dump(customers)), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch customers", "details": str(e)}), 500


@customers_bp.route("/<int:id>", methods=["GET"])
def get_customer(id):
    try:
        customer = Customer.query.get(id)
        if not customer:
            return jsonify({"error": f"Customer with id {id} not found"}), 404
        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch customer", "details": str(e)}), 500


@customers_bp.route("/", methods=["POST"])
def create_customer():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        validated = customer_schema.load(data)

        if Customer.query.filter_by(email=validated["email"]).first():
            return jsonify({"error": f"Email '{validated['email']}' already exists"}), 409

        customer = Customer(**validated)
        db.session.add(customer)
        db.session.commit()
        return jsonify(customer_schema.dump(customer)), 201

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create customer", "details": str(e)}), 500


@customers_bp.route("/<int:id>", methods=["DELETE"])
def delete_customer(id):
    try:
        customer = Customer.query.get(id)
        if not customer:
            return jsonify({"error": f"Customer with id {id} not found"}), 404

        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": f"Customer {id} deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete customer", "details": str(e)}), 500
