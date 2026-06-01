from flask import jsonify, request
from marshmallow import ValidationError
from . import products_bp
from .models import Product
from .schemas import product_schema, products_schema, product_update_schema
from app.extensions import db
from app.logger import setup_logger

logger = setup_logger(__name__)


@products_bp.route("/", methods=["GET"])
def get_products():
    try:
        logger.debug("Fetching all products")
        products = Product.query.all()
        logger.debug(f"Returned {len(products)} products")
        return jsonify(products_schema.dump(products)), 200
    except Exception as e:
        logger.error(f"Failed to fetch products: {e}")
        return jsonify({"error": "Failed to fetch products", "details": str(e)}), 500


@products_bp.route("/<int:id>", methods=["GET"])
def get_product(id):
    try:
        logger.debug(f"Fetching product id={id}")
        product = Product.query.get(id)
        if not product:
            logger.warning(f"Product id={id} not found")
            return jsonify({"error": f"Product with id {id} not found"}), 404
        return jsonify(product_schema.dump(product)), 200
    except Exception as e:
        logger.error(f"Failed to fetch product id={id}: {e}")
        return jsonify({"error": "Failed to fetch product", "details": str(e)}), 500


@products_bp.route("/", methods=["POST"])
def create_product():
    try:
        data = request.get_json()
        if not data:
            logger.warning("Create product called with empty body")
            return jsonify({"error": "Request body must be JSON"}), 400

        validated = product_schema.load(data)

        if Product.query.filter_by(sku=validated["sku"]).first():
            logger.warning(f"Duplicate SKU attempted: {validated['sku']}")
            return jsonify({"error": f"SKU '{validated['sku']}' already exists"}), 409

        product = Product(**validated)
        db.session.add(product)
        db.session.commit()
        logger.debug(f"Product created: id={product.id} sku={product.sku}")
        return jsonify(product_schema.dump(product)), 201

    except ValidationError as e:
        logger.warning(f"Product validation failed: {e.messages}")
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create product: {e}")
        return jsonify({"error": "Failed to create product", "details": str(e)}), 500


@products_bp.route("/<int:id>", methods=["PUT"])
def update_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            logger.warning(f"Update attempted on non-existent product id={id}")
            return jsonify({"error": f"Product with id {id} not found"}), 404

        data = request.get_json()
        if not data:
            logger.warning("Update product called with empty body")
            return jsonify({"error": "Request body must be JSON"}), 400

        validated = product_update_schema.load(data)

        if "sku" in validated and validated["sku"] != product.sku:
            if Product.query.filter_by(sku=validated["sku"]).first():
                logger.warning(f"Duplicate SKU on update: {validated['sku']}")
                return jsonify({"error": f"SKU '{validated['sku']}' already exists"}), 409

        for key, value in validated.items():
            setattr(product, key, value)

        db.session.commit()
        logger.debug(f"Product updated: id={id}")
        return jsonify(product_schema.dump(product)), 200

    except ValidationError as e:
        logger.warning(f"Product update validation failed: {e.messages}")
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update product id={id}: {e}")
        return jsonify({"error": "Failed to update product", "details": str(e)}), 500


@products_bp.route("/<int:id>", methods=["DELETE"])
def delete_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            logger.warning(f"Delete attempted on non-existent product id={id}")
            return jsonify({"error": f"Product with id {id} not found"}), 404

        db.session.delete(product)
        db.session.commit()
        logger.debug(f"Product deleted: id={id}")
        return jsonify({"message": f"Product {id} deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete product id={id}: {e}")
        return jsonify({"error": "Failed to delete product", "details": str(e)}), 500
