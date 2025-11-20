# database/connection.py

from flask_pymongo import PyMongo

# ---------------------------------------------------------
# GLOBAL MONGO INSTANCE
#
# This PyMongo object will be shared across the entire app.
# It gets initialized with app settings inside init_db().
#
# Usage pattern:
#     from database.connection import mongo
#     mongo.db.collection_name.find(...)
# ---------------------------------------------------------
mongo = PyMongo()


def init_db(app):
    """
    Initialize MongoDB connection for the Flask application.
    This must be called inside create_app() before any blueprints
    attempt to access the database.

    After initialization, the global 'mongo' object becomes active
    and mongo.db will be available throughout the application.

    Example usage:
        def create_app():
            app = Flask(__name__)
            init_db(app)
            ...
    """

    # -----------------------------------------------------
    # MONGO CONNECTION STRING
    #
    # This connects to a local MongoDB instance:
    #     mongodb://localhost:27017/
    #
    # The database name used here is:
    #     timeless_threads
    #
    # NOTE:
    #   - If you use authentication, add username/password.
    #   - For MongoDB Atlas, paste your cloud connection string.
    # -----------------------------------------------------
    app.config["MONGO_URI"] = "mongodb://localhost:27017/timeless_threads"

    # -----------------------------------------------------
    # Initialize PyMongo with the app configuration
    # -----------------------------------------------------
    mongo.init_app(app)

    # Confirmation message for development use
    print("✔ MongoDB connected successfully!")
