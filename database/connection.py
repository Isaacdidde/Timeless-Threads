# database/connection.py

from flask import current_app
from pymongo import MongoClient, errors as mongo_errors

mongo_client = None   # Shared connection pool


# =====================================================================
# INIT DB (called only from app_factory)
# =====================================================================
def init_db(app):
    """
    Initialize MongoDB using MongoClient and attach the DB to the Flask app.
    This MUST run inside app context → AppFactory guarantees that.
    """

    global mongo_client

    mongo_uri = app.config.get("MONGO_URI")
    db_name = app.config.get("MONGO_DB_NAME")

    if not mongo_uri:
        raise RuntimeError("❌ Missing MONGO_URI in config or .env file")

    if not db_name:
        raise RuntimeError("❌ Missing MONGO_DB_NAME in config or .env file")

    try:
        mongo_client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=3000,
            maxPoolSize=50
        )

        # Ping server — ensures connection is valid
        mongo_client.admin.command("ping")

        # Attach DB object to Flask app
        app.db = mongo_client[db_name]

        print(f"✔ MongoDB connected → {mongo_uri}/{db_name}")

    except mongo_errors.ServerSelectionTimeoutError:
        raise RuntimeError("❌ MongoDB timeout — cluster not reachable")

    except mongo_errors.ConnectionFailure:
        raise RuntimeError("❌ MongoDB connection failure")

    except Exception as e:
        print("❌ Unexpected MongoDB initialization error:", e)
        raise


# =====================================================================
# GET DB (safe inside app context)
# =====================================================================
def get_db():
    """
    Returns the active Mongo DB object.
    Works ONLY inside Flask request/app context.
    """

    try:
        db = getattr(current_app, "db", None)
        if db is None:
            raise RuntimeError("DB not attached to Flask app. Call init_db(app).")
        return db

    except RuntimeError:
        # This error occurs when current_app is unavailable (CLI, scripts)
        raise RuntimeError("No Flask app context available — cannot access DB.")


# =====================================================================
# GET COLLECTION (used everywhere)
# =====================================================================
def get_collection(name):
    """
    Safely returns a collection from the database.
    Example: get_collection("products")
    """

    try:
        db = get_db()
        return db[name]

    except Exception as e:
        print(f"❌ ERROR: Cannot access collection '{name}':", e)
        raise


# =====================================================================
# BACKWARD COMPATIBILITY FOR: mongo.db.collection
# =====================================================================
class MongoWrapper:
    @property
    def db(self):
        return get_db()


mongo = MongoWrapper()
