# database/connection.py

from flask import current_app
from pymongo import MongoClient, errors as mongo_errors

mongo_client = None  # Global pool reference (thread-safe creation)


# =====================================================================
# INIT DB
# =====================================================================
def init_db(app):
    """
    Initialize MongoDB and attach database instance to Flask app.
    This runs inside app.app_context(), so current_app is safe.
    """

    global mongo_client

    mongo_uri = app.config.get("MONGO_URI")
    db_name = app.config.get("MONGO_DB_NAME")

    if not mongo_uri:
        raise RuntimeError("❌ MONGO_URI is missing from settings or .env")

    if not db_name:
        raise RuntimeError("❌ MONGO_DB_NAME is missing from settings or .env")

    try:
        # Create a new shared Mongo client connection pool
        mongo_client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,    # Fail fast if unreachable
            connectTimeoutMS=3000,
            maxPoolSize=50
        )

        # Validate connection by pinging server
        mongo_client.admin.command("ping")

        # Attach DB reference to the Flask app
        app.db = mongo_client[db_name]

        print(f"✔ MongoDB connected → {mongo_uri}/{db_name}")

    except mongo_errors.ServerSelectionTimeoutError:
        msg = "❌ MongoDB connection timeout — check network / cluster status"
        print(msg)
        raise RuntimeError(msg)

    except mongo_errors.ConnectionFailure:
        msg = "❌ MongoDB connection failure — could not connect to server"
        print(msg)
        raise RuntimeError(msg)

    except Exception as e:
        print("❌ Unexpected MongoDB Initialization Error:", e)
        raise



# =====================================================================
# GET DB
# =====================================================================
def get_db():
    """
    Returns the current MongoDB database object.
    Works inside request context or app context only.
    """

    try:
        db = getattr(current_app, "db", None)
        if not db:
            raise RuntimeError("Database not initialized. Call init_db(app) first.")
        return db
    except RuntimeError:
        # current_app is unavailable (CLI, scripts)
        raise RuntimeError("No Flask app context available for DB access.")



# =====================================================================
# GET COLLECTION
# =====================================================================
def get_collection(name):
    """
    Returns a MongoDB collection safely.
    Example: get_collection("products")
    """

    try:
        db = get_db()
        return db[name]
    except KeyError:
        print(f"❌ ERROR: Collection '{name}' does not exist in database.")
        raise
    except Exception as e:
        print(f"❌ ERROR: Failed to access collection '{name}':", e)
        raise



# =====================================================================
# BACKWARD COMPATIBILITY
# Allows legacy syntax: mongo.db.products
# =====================================================================

class MongoWrapper:
    @property
    def db(self):
        try:
            return get_db()
        except Exception as e:
            print("❌ ERROR: Legacy mongo.db access failed:", e)
            raise


mongo = MongoWrapper()
