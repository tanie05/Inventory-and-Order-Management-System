from flask import jsonify, request
from marshmallow import ValidationError
from . import products_bp
from .models import Product
from .schemas import product_schema, products_schema, product_update_schema
from app.extensions import db


@products_bp.route("/", methods=["GET"])
def get_products():
    try:
        products = Product.query.all()
        return jsonify(products_schema.dump(products)), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch products", "details": str(e)}), 500


@products_bp.route("/<int:id>", methods=["GET"])
def get_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({"error": f"Product with id {id} not found"}), 404
        return jsonify(product_schema.dump(product)), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch product", "details": str(e)}), 500


@products_bp.route("/", methods=["POST"])
def create_product():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        validated = product_schema.load(data)

        if Product.query.filter_by(sku=validated["sku"]).first():
            return jsonify({"error": f"SKU '{validated['sku']}' already exists"}), 409

        product = Product(**validated)
        db.session.add(product)
        db.session.commit()
        return jsonify(product_schema.dump(product)), 201

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create product", "details": str(e)}), 500


@products_bp.route("/<int:id>", methods=["PUT"])
def update_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({"error": f"Product with id {id} not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        validated = product_update_schema.load(data)

        if "sku" in validated and validated["sku"] != product.sku:
            if Product.query.filter_by(sku=validated["sku"]).first():
                return jsonify({"error": f"SKU '{validated['sku']}' already exists"}), 409

        for key, value in validated.items():
            setattr(product, key, value)

        db.session.commit()
        return jsonify(product_schema.dump(product)), 200

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update product", "details": str(e)}), 500


@products_bp.route("/<int:id>", methods=["DELETE"])
def delete_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({"error": f"Product with id {id} not found"}), 404

        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": f"Product {id} deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete product", "details": str(e)}), 500
