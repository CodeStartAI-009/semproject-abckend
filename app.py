from flask import Flask
from flask_cors import CORS

# 🔹 Import Blueprints
from routes.auth_routes import auth
from routes.movie_routes import movie
from routes.review_routes import review


def create_app():
    app = Flask(__name__)

    # 🔥 Enable CORS (allow frontend access)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # 🔹 Register Blueprints
    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(movie, url_prefix="/api")
    app.register_blueprint(review, url_prefix="/api")

    return app


# 🚀 Run Server
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)