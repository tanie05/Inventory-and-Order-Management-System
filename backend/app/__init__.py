from flask import Flask, jsonify
from .extensions import db, migrate
from .config import DATABASE_URL


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from .products import products_bp
    from .products.models import Product
    from .customers import customers_bp
    from .customers.models import Customer
    from .orders import orders_bp
    from .orders.models import Order, OrderItem

    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(customers_bp, url_prefix="/api/customers")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")

    @app.route("/")
    def index():
        return jsonify({"message": "Hello World"})

    return app


