import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


# ================================================================
# BASE CONFIG (used by ALL environments)
# ================================================================
class Config:
    """
    Base configuration class.
    Shared settings for both Development and Production.
    """

    # -----------------------------
    # Flask core settings
    # -----------------------------
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "unsafe-dev-key")

    DEBUG = False  # Production default

    # -----------------------------
    # MongoDB
    # -----------------------------
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "timeless_threads")

    # -----------------------------
    # Admin seed credentials
    # -----------------------------
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    # -----------------------------
    # Ads System
    # -----------------------------
    ADS_SYSTEM_ENABLED = (
        os.getenv("ADS_SYSTEM_ENABLED", "true").lower() == "true"
    )

    # Default ad slot for fallbacks
    ADS_DEFAULT_SLOT = "homepage_hero"

    # -----------------------------
    # External microservices (DCORP)
    # -----------------------------
    DCORP_API_URL = os.getenv("DCORP_API_URL")

    # -----------------------------
    # Cookie & Security Settings
    # -----------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True  # Force HTTPS cookies in production

    # Optional: security headers (can be added via middleware)
    ENABLE_SECURITY_HEADERS = True


# ================================================================
# DEVELOPMENT CONFIG
# ================================================================
class DevelopmentConfig(Config):
    """
    Development environment:
    - Debug enabled
    - Uses local fallbacks
    """

    DEBUG = True

    # More permissive session handling in dev
    SESSION_COOKIE_SECURE = False

    # Fallback secrets for local dev
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

    # Local MongoDB fallback
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017/timeless_threads"
    )

    # Local DCORP backend (Dev mode)
    DCORP_API_URL = os.getenv("DCORP_API_URL", "http://localhost:5000")


# ================================================================
# PRODUCTION CONFIG
# ================================================================
class ProductionConfig(Config):
    """
    Production environment:
    - Debug disabled
    - Requires proper env variables
    """

    DEBUG = False

    # Production requires strict cookies
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Fail-safe: prevent starting without essential configs
    if not os.getenv("FLASK_SECRET_KEY"):
        raise RuntimeError("❌ Missing FLASK_SECRET_KEY in environment!")

    if not os.getenv("MONGO_URI"):
        raise RuntimeError("❌ Missing MONGO_URI in environment!")

    if not os.getenv("DCORP_API_URL"):
        raise RuntimeError("❌ Missing DCORP_API_URL in environment!")
