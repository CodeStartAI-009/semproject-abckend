from flask import Blueprint, request, jsonify
from models.db import users
import bcrypt
from utils.jwt_handler import generate_token

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["POST"])
def register():
    data = request.json

    hashed_pw = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())

    user = {
        "username": data["username"],
        "email": data["email"],
        "password": hashed_pw
    }

    users.insert_one(user)
    return jsonify({"message": "User registered"})


@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    user = users.find_one({"email": data["email"]})

    if not user:
        return jsonify({"error": "User not found"}), 404

    if bcrypt.checkpw(data["password"].encode(), user["password"]):
        token = generate_token(user["_id"])
        return jsonify({"token": token})

    return jsonify({"error": "Invalid password"}), 401