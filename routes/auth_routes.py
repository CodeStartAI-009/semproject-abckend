from flask import Blueprint, request, jsonify
from models.db import users
import bcrypt
from utils.jwt_handler import generate_token

auth = Blueprint("auth", __name__)


# 🔐 REGISTER
@auth.route("/register", methods=["POST"])
def register():
    try:
        if users is None:
            return jsonify({"error": "Database not connected"}), 500

        data = request.json

        # 🔥 Validation
        if not data.get("username") or not data.get("email") or not data.get("password"):
            return jsonify({"error": "All fields are required"}), 400

        # 🔥 Check duplicate user
        existing_user = users.find_one({"email": data["email"]})
        if existing_user:
            return jsonify({"error": "User already exists"}), 400

        # 🔥 Hash password
        hashed_pw = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())

        user = {
            "username": data["username"],
            "email": data["email"],
            "password": hashed_pw  # stored as bytes (OK)
        }

        users.insert_one(user)

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        print("❌ Register Error:", e)
        return jsonify({"error": "Internal server error"}), 500


# 🔐 LOGIN
@auth.route("/login", methods=["POST"])
def login():
    try:
        if users is None:
            return jsonify({"error": "Database not connected"}), 500

        data = request.json

        # 🔥 Validation
        if not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password required"}), 400

        user = users.find_one({"email": data["email"]})

        if not user:
            return jsonify({"error": "User not found"}), 404

        # 🔥 Check password
        if bcrypt.checkpw(data["password"].encode(), user["password"]):
            token = generate_token(user["_id"])

            return jsonify({
                "message": "Login successful",
                "token": token,
                "username": user["username"]
            }), 200

        return jsonify({"error": "Invalid password"}), 401

    except Exception as e:
        print("❌ Login Error:", e)
        return jsonify({"error": "Internal server error"}), 500