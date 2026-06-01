from flask import Flask, jsonify
from .extensions import db
from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from .products import products_bp
    from .customers import customers_bp
    from .orders import orders_bp

    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(customers_bp, url_prefix="/api/customers")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")

    @app.route("/")
    def index():
        return jsonify({"message": "Hello World"})

    return app
