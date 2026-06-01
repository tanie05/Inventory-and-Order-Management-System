from flask import jsonify
from . import products_bp
from .models import Product


@products_bp.route("/", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products]), 200
