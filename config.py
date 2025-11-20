import os
from dotenv import load_dotenv

# -------------------------------------------------------------
# Load environment variables from a .env file (if present)
# Makes sensitive data like SECRET_KEY and DB URI configurable
# without hard-coding them in source code.
# -------------------------------------------------------------
load_dotenv()


class DevelopmentConfig:
    """
    Configuration class used during development.

    Values are loaded from environment variables so you can keep:
      - secret keys
      - database URIs
      - API tokens
    outside your source code repository.
    """

    # Enable Flask debugging (auto reload + detailed error pages)
    DEBUG = True

    # Secret key for session signing & CSRF protection
    # Stored in .env as FLASK_SECRET_KEY
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # MongoDB connection URI
    # Stored in .env as MONGO_URI
    MONGO_URI = os.getenv("MONGO_URI")
