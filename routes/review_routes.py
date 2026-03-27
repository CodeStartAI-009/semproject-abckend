from flask import Blueprint, request, jsonify
from models.db import reviews
from utils.jwt_handler import decode_token
from utils.sentiment import analyze_reviews

from datetime import datetime
from textblob import TextBlob

review = Blueprint("review", __name__)


# 🔐 Get user from JWT (SAFE)
def get_user_id(req):
    auth_header = req.headers.get("Authorization")

    if not auth_header:
        return None

    try:
        token = auth_header.split(" ")[1]
        decoded = decode_token(token)

        if not decoded:
            return None

        return decoded["user_id"]

    except Exception as e:
        print("AUTH ERROR:", e)
        return None


# 📥 Get ALL reviews (FULL DETAILS)
@review.route("/reviews/<movie_id>", methods=["GET"])
def get_reviews(movie_id):
    try:
        data = []

        for r in reviews.find({"movie_id": str(movie_id)}):
            review_obj = {
                "_id": str(r["_id"]),
                "user_id": r.get("user_id"),
                "rating": r.get("rating"),
                "review_text": r.get("review_text"),
                "created_at": r.get("created_at"),
                "sentiment": r.get("sentiment", "N/A")
            }

            data.append(review_obj)

        return jsonify(data)

    except Exception as e:
        print("ERROR in get_reviews:", e)
        return jsonify({"error": str(e)}), 500


# ➕ Add review (FULL VERSION)
@review.route("/reviews", methods=["POST"])
def add_review():
    try:
        data = request.json
        user_id = get_user_id(request)

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # 🚫 Prevent duplicate review
        existing = reviews.find_one({
            "user_id": user_id,
            "movie_id": str(data["movie_id"])
        })

        if existing:
            return jsonify({"error": "You already reviewed this movie"}), 400

        # 🔥 Sentiment Analysis
        text = data["review_text"]
        polarity = TextBlob(text).sentiment.polarity
        sentiment = "positive" if polarity >= 0 else "negative"

        review_data = {
            "user_id": user_id,
            "movie_id": str(data["movie_id"]),
            "rating": int(data["rating"]),
            "review_text": text,
            "created_at": datetime.utcnow().isoformat(),  # 🔥 timestamp
            "sentiment": sentiment
        }

        reviews.insert_one(review_data)

        return jsonify({"message": "Review added"})

    except Exception as e:
        print("ERROR in add_review:", e)
        return jsonify({"error": str(e)}), 500


# 📊 ML Summary (overall analysis)
@review.route("/reviews/summary/<movie_id>", methods=["GET"])
def review_summary(movie_id):
    try:
        movie_reviews = list(reviews.find({"movie_id": str(movie_id)}))
        summary = analyze_reviews(movie_reviews)
        return jsonify(summary)

    except Exception as e:
        print("ERROR in summary:", e)
        return jsonify({"error": str(e)}), 500