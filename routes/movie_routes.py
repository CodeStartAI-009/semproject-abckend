from flask import Blueprint, jsonify, request
import requests
from config import TMDB_API_KEY

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

movie = Blueprint("movie", __name__)

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


# 🔥 Create session with retry (fix connection reset)
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)


# 🎬 Get Movies (pagination + category)
@movie.route("/movies", methods=["GET"])
def get_movies():
    try:
        if not TMDB_API_KEY:
            return jsonify({"error": "API key missing"}), 500

        page = int(request.args.get("page", 1))
        category = request.args.get("category", "popular")

        # 🎯 Select correct endpoint
        if category == "top_rated":
            url = f"{BASE_URL}/movie/top_rated?api_key={TMDB_API_KEY}&page={page}"

        elif category == "trending":
            # ❌ trending doesn't support page
            url = f"{BASE_URL}/trending/movie/day?api_key={TMDB_API_KEY}"

        else:
            url = f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&page={page}"

        print("🔥 URL:", url)

        # ✅ Safe request
        res = session.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        print("🔥 STATUS:", res.status_code)

        if res.status_code != 200:
            print("TMDB ERROR:", res.text)
            return jsonify({"error": "TMDB API failed"}), 500

        data = res.json()

        movies = []

        for m in data.get("results", []):
            movies.append({
                "_id": str(m.get("id")),
                "title": m.get("title"),
                "description": m.get("overview"),
                "poster": f"{IMAGE_BASE}{m['poster_path']}" if m.get("poster_path") else None,
                "rating": m.get("vote_average")
            })

        return jsonify(movies)

    except Exception as e:
        print("❌ ERROR in /movies:", e)
        return jsonify({"error": str(e)}), 500


# 🎥 Get Single Movie Details
@movie.route("/movies/<id>", methods=["GET"])
def get_movie(id):
    try:
        if not TMDB_API_KEY:
            return jsonify({"error": "API key missing"}), 500

        url = f"{BASE_URL}/movie/{id}?api_key={TMDB_API_KEY}"

        res = session.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        if res.status_code != 200:
            print("TMDB ERROR:", res.text)
            return jsonify({"error": "Movie not found"}), 404

        m = res.json()

        return jsonify({
            "_id": str(m.get("id")),
            "title": m.get("title"),
            "description": m.get("overview"),
            "poster": f"{IMAGE_BASE}{m['poster_path']}" if m.get("poster_path") else None,
            "rating": m.get("vote_average"),
            "release_date": m.get("release_date"),
            "genres": [g["name"] for g in m.get("genres", [])]
        })

    except Exception as e:
        print("❌ ERROR in /movies/<id>:", e)
        return jsonify({"error": str(e)}), 500