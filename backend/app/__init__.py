from flask import Flask, jsonify
from .extensions import db, migrate, limiter, jwt
from .config import DATABASE_URL, JWT_SECRET_KEY


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    jwt.init_app(app)

    from .auth import auth_bp
    from .products import products_bp
    from .products.models import Product
    from .customers import customers_bp
    from .customers.models import Customer
    from .orders import orders_bp
    from .orders.models import Order, OrderItem

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(customers_bp, url_prefix="/api/customers")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")

    @app.route("/")
    def index():
        return jsonify({"message": "Hello World"})

    return app
