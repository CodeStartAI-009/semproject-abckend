from flask import Blueprint, request, jsonify
from models.db import reviews
from utils.jwt_handler import decode_token
from utils.sentiment import analyze_reviews
from utils.ml_sentiment import predict_sentiment

from datetime import datetime
import requests
from config import TMDB_API_KEY

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

review = Blueprint("review", __name__)

BASE_URL = "https://api.themoviedb.org/3"


# 🔥 Create session with retry (IMPORTANT)
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)


# 🎬 Fetch TMDB Reviews + ML Sentiment
def fetch_tmdb_reviews(movie_id):
    try:
        if not TMDB_API_KEY:
            return []

        url = f"{BASE_URL}/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}"

        res = session.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        if res.status_code != 200:
            print("TMDB ERROR:", res.text)
            return []

        data = res.json()
        tmdb_reviews = []

        for r in data.get("results", []):
            text = r.get("content", "")

            tmdb_reviews.append({
                "user_id": r.get("author"),
                "rating": r.get("author_details", {}).get("rating") or 5,  # ✅ FIXED
                "review_text": text,
                "created_at": r.get("created_at"),
                "sentiment": predict_sentiment(text),
                "source": "tmdb"
            })

        return tmdb_reviews

    except Exception as e:
        print("TMDB REVIEW ERROR:", e)
        return []


# 🔐 Get user from JWT
def get_user_id(req):
    auth_header = req.headers.get("Authorization")

    if not auth_header:
        return None

    try:
        token = auth_header.split(" ")[1]
        decoded = decode_token(token)

        return decoded.get("user_id") if decoded else None

    except Exception as e:
        print("AUTH ERROR:", e)
        return None


# 📥 Get ALL reviews (DB + TMDB)
@review.route("/reviews/<movie_id>", methods=["GET"])
def get_reviews(movie_id):
    try:
        data = []

        # 🔹 DB Reviews
        db_reviews = list(reviews.find({"movie_id": str(movie_id)}))

        for r in db_reviews:
            data.append({
                "_id": str(r["_id"]),
                "user_id": r.get("user_id"),
                "rating": r.get("rating"),
                "review_text": r.get("review_text"),
                "created_at": r.get("created_at"),
                "sentiment": r.get("sentiment", "N/A"),
                "source": "user"
            })

        # 🔹 TMDB Reviews
        tmdb_reviews = fetch_tmdb_reviews(movie_id)

        # 🔥 Combine
        data.extend(tmdb_reviews)

        return jsonify(data)

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ➕ Add Review (ML Sentiment)
@review.route("/reviews", methods=["POST"])
def add_review():
    try:
        data = request.json

        # 🔒 Validate input
        if not data or "movie_id" not in data or "review_text" not in data or "rating" not in data:
            return jsonify({"error": "Missing required fields"}), 400

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

        text = data["review_text"]

        # 🔥 ML Sentiment
        sentiment = predict_sentiment(text)

        review_data = {
            "user_id": user_id,
            "movie_id": str(data["movie_id"]),
            "rating": float(data["rating"]),
            "review_text": text,
            "created_at": datetime.utcnow().isoformat(),
            "sentiment": sentiment,
            "source": "user"
        }

        reviews.insert_one(review_data)

        return jsonify({
            "message": "Review added successfully",
            "sentiment": sentiment
        })

    except Exception as e:
        print("ERROR in add_review:", e)
        return jsonify({"error": str(e)}), 500


# 📊 Review Summary (Combined)
@review.route("/reviews/summary/<movie_id>", methods=["GET"])
def review_summary(movie_id):
    try:
        # 🔹 DB Reviews
        db_reviews = list(reviews.find({"movie_id": str(movie_id)}))

        # 🔹 TMDB Reviews
        tmdb_reviews = fetch_tmdb_reviews(movie_id)

        # 🔥 Combine all
        all_reviews = db_reviews + tmdb_reviews

        # 🔥 Analyze (your upgraded function)
        summary = analyze_reviews(all_reviews)

        return jsonify(summary)

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500