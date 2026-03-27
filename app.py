from flask import Flask
from flask_cors import CORS

from routes.auth_routes import auth
from routes.movie_routes import movie
from routes.review_routes import review

app = Flask(__name__)

# 🔥 FIX CORS HERE
CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(auth)
app.register_blueprint(movie)
app.register_blueprint(review)

if __name__ == "__main__":
    app.run(debug=True)