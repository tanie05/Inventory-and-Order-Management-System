from flask import jsonify, request
from . import products_bp
from .models import Product
from app.extensions import db


@products_bp.route("/", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products]), 200


@products_bp.route("/<int:id>", methods=["GET"])
def get_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict()), 200


@products_bp.route("/", methods=["POST"])
def create_product():
    data = request.get_json()

    if not data.get("name") or not data.get("sku") or not data.get("price"):
        return jsonify({"error": "name, sku and price are required"}), 400

    if data.get("price") < 0 or data.get("stock_quantity", 0) < 0:
        return jsonify({"error": "price and stock_quantity cannot be negative"}), 400

    if Product.query.filter_by(sku=data["sku"]).first():
        return jsonify({"error": "SKU already exists"}), 409

    product = Product(
        name=data["name"],
        sku=data["sku"],
        description=data.get("description"),
        price=data["price"],
        stock_quantity=data.get("stock_quantity", 0),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@products_bp.route("/<int:id>", methods=["PUT"])
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()

    if "price" in data and data["price"] < 0:
        return jsonify({"error": "price cannot be negative"}), 400

    if "stock_quantity" in data and data["stock_quantity"] < 0:
        return jsonify({"error": "stock_quantity cannot be negative"}), 400

    if "sku" in data and data["sku"] != product.sku:
        if Product.query.filter_by(sku=data["sku"]).first():
            return jsonify({"error": "SKU already exists"}), 409

    product.name = data.get("name", product.name)
    product.sku = data.get("sku", product.sku)
    product.description = data.get("description", product.description)
    product.price = data.get("price", product.price)
    product.stock_quantity = data.get("stock_quantity", product.stock_quantity)

    db.session.commit()
    return jsonify(product.to_dict()), 200


@products_bp.route("/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"Product {id} deleted"}), 200
