from pymongo import MongoClient

client = MongoClient("mongodb+srv://unispend001_db_user:EN4FlDzyNNssWJvy@artarena.dt76rg8.mongodb.net/movie?retryWrites=true&w=majority")
db = client["movie_db"]

users = db["users"]
movies = db["movies"]
reviews = db["reviews"]