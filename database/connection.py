import os
from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    """
    Initialize MongoDB using environment variable MONGO_URI.
    If not provided, fallback to local MongoDB.
    """

    # Use environment variable if available
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        print("⚠ WARNING: MONGO_URI missing! Using localhost.")
        mongo_uri = "mongodb://localhost:27017/timeless_threads"

    app.config["MONGO_URI"] = mongo_uri

    # Initialize Mongo
    mongo.init_app(app)

    print(f"✔ MongoDB connected to: {mongo_uri}")
