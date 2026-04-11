from pymongo import MongoClient
from config import MONGO_URI

try:
    # 🔥 Connect to MongoDB Atlas
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

    # 🔥 Force connection test
    client.server_info()

    db = client["movie_db"]

    users = db["users"]
    movies = db["movies"]
    reviews = db["reviews"]

    print("✅ MongoDB Connected Successfully")

except Exception as e:
    print("❌ MongoDB Connection Error:", e)

    # 🔥 Prevent import crash
    users = None
    movies = None
    reviews = None