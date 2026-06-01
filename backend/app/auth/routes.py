from flask import jsonify, request
from flask_jwt_extended import create_access_token
from datetime import timedelta
import bcrypt
from . import auth_bp
from app.config import ADMIN_EMAIL, ADMIN_PW
from app.logger import setup_logger

logger = setup_logger(__name__)

# hash the admin password once at import time
ADMIN_PW_HASH = bcrypt.hashpw(ADMIN_PW.encode("utf-8"), bcrypt.gensalt())


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        logger.warning("Login attempt with missing credentials")
        return jsonify({"error": "email and password are required"}), 400

    if data["email"] != ADMIN_EMAIL:
        logger.warning(f"Login failed - unknown email: {data['email']}")
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.checkpw(data["password"].encode("utf-8"), ADMIN_PW_HASH):
        logger.warning(f"Login failed - wrong password for: {data['email']}")
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=data["email"], expires_delta=timedelta(hours=24))
    logger.debug(f"Login successful for: {data['email']}")
    return jsonify({"access_token": token}), 200
