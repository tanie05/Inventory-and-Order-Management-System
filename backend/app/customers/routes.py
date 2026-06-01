from flask import jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from . import customers_bp
from .models import Customer
from .schemas import customer_schema, customers_schema
from app.extensions import db
from app.logger import setup_logger

logger = setup_logger(__name__)


@customers_bp.route("/", methods=["GET"])
@jwt_required()
def get_customers():
    try:
        logger.debug("Fetching all customers")
        customers = Customer.query.all()
        logger.debug(f"Returned {len(customers)} customers")
        return jsonify(customers_schema.dump(customers)), 200
    except Exception as e:
        logger.error(f"Failed to fetch customers: {e}")
        return jsonify({"error": "Failed to fetch customers", "details": str(e)}), 500


@customers_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_customer(id):
    try:
        logger.debug(f"Fetching customer id={id}")
        customer = Customer.query.get(id)
        if not customer:
            logger.warning(f"Customer id={id} not found")
            return jsonify({"error": f"Customer with id {id} not found"}), 404
        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        logger.error(f"Failed to fetch customer id={id}: {e}")
        return jsonify({"error": "Failed to fetch customer", "details": str(e)}), 500


@customers_bp.route("/", methods=["POST"])
@jwt_required()
def create_customer():
    try:
        data = request.get_json()
        if not data:
            logger.warning("Create customer called with empty body")
            return jsonify({"error": "Request body must be JSON"}), 400

        validated = customer_schema.load(data)

        if Customer.query.filter_by(email=validated["email"]).first():
            logger.warning(f"Duplicate email attempted: {validated['email']}")
            return jsonify({"error": f"Email '{validated['email']}' already exists"}), 409

        customer = Customer(**validated)
        db.session.add(customer)
        db.session.commit()
        logger.debug(f"Customer created: id={customer.id} email={customer.email}")
        return jsonify(customer_schema.dump(customer)), 201

    except ValidationError as e:
        logger.warning(f"Customer validation failed: {e.messages}")
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create customer: {e}")
        return jsonify({"error": "Failed to create customer", "details": str(e)}), 500


@customers_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_customer(id):
    try:
        customer = Customer.query.get(id)
        if not customer:
            logger.warning(f"Delete attempted on non-existent customer id={id}")
            return jsonify({"error": f"Customer with id {id} not found"}), 404

        db.session.delete(customer)
        db.session.commit()
        logger.debug(f"Customer deleted: id={id}")
        return jsonify({"message": f"Customer {id} deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete customer id={id}: {e}")
        return jsonify({"error": "Failed to delete customer", "details": str(e)}), 500
