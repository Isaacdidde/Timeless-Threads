# app_factory.py

import os
import logging
from flask import Flask

from config import Config, DevelopmentConfig
from seed_admin import seed_admin_user

from database.connection import init_db



class AppFactory:
    """
    Factory for creating and configuring the Flask application.

    Boot sequence:
        1. Load base configuration
        2. Initialize MongoDB
        3. Configure Jinja2
        4. Register context processors
        5. Register blueprints
        6. Seed admin user (safe)
    """

    def __init__(self, config_class=DevelopmentConfig):
        self.config_class = config_class

        # Flask instance setup
        self.app = Flask(__name__, instance_relative_config=True)

        # Default logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("timeless_threads")

        # Set default DCORP backend URL — overrideable via environment
        self.app.config["DCORP_API_URL"] = os.getenv(
            "DCORP_API_URL",
            "http://127.0.0.1:5000"  # development fallback
        )

    # ------------------------------------------------------
    # CONFIGURATION LOADING
    # ------------------------------------------------------
    def load_config(self):
        """Load config objects and optional instance overrides."""
        self.app.config.from_object(self.config_class)

        # Ensure the instance folder exists
        os.makedirs(self.app.instance_path, exist_ok=True)

        # Load instance/config.py if present
        instance_config_path = os.path.join(self.app.instance_path, "config.py")
        if os.path.exists(instance_config_path):
            try:
                self.app.config.from_pyfile("config.py")
                self.logger.info("Loaded instance config overrides.")
            except Exception as err:
                self.logger.warning("Failed loading instance config → %s", err)

        # Expose global settings object
        self.app.config["SETTINGS"] = Config

        # Log mode
        self.logger.info("Configuration loaded (%s)", self.config_class.__name__)

    # ------------------------------------------------------
    # DATABASE INITIALIZATION
    # ------------------------------------------------------
    def init_extensions(self):
        """Initialize MongoDB and any other extensions."""
        try:
            init_db(self.app)
            self.logger.info("MongoDB connected successfully.")
        except Exception as err:
            self.logger.error("MongoDB initialization failed → %s", err)
            raise

    # ------------------------------------------------------
    # JINJA TEMPLATE ENGINE CONFIG
    # ------------------------------------------------------
    def init_jinja(self):
        """Enable whitespace control and custom Jinja settings."""
        env = self.app.jinja_env
        env.trim_blocks = True
        env.lstrip_blocks = True
        self.logger.info("Jinja environment configured.")

    # ------------------------------------------------------
    # CONTEXT PROCESSORS
    # ------------------------------------------------------
    def init_context_processors(self):
        """Register global context processors (categories, ads, user info)."""
        try:
            from controllers.main_controller import register_context_processors
            register_context_processors(self.app)
            self.logger.info("Context processors registered.")
        except Exception as err:
            self.logger.error("Context processor registration failed → %s", err)

    # ------------------------------------------------------
    # BLUEPRINT REGISTRATION
    # ------------------------------------------------------
    def init_blueprints(self):
        """Load all blueprints from routes/__init__.py."""
        try:
            from routes import register_blueprints
            register_blueprints(self.app)
            self.logger.info("Blueprints registered.")
        except Exception as err:
            self.logger.error("Blueprint registration failed → %s", err)
            raise

    # ------------------------------------------------------
    # FACTORY ENTRY POINT
    # ------------------------------------------------------
    def create_app(self):
        """Run the full boot process and return the Flask app instance."""
        # 1. Load Core Config
        self.load_config()

        # 2. Initialize database
        self.init_extensions()

        # 3. Jinja engine setup
        self.init_jinja()

        # 4. Global context processors
        self.init_context_processors()

        # 5. Register blueprints
        self.init_blueprints()

        # 6. Seed admin user safely (only once)
        with self.app.app_context():
            try:
                seed_admin_user()
                self.logger.info("Admin seed complete.")
            except Exception as err:
                self.logger.warning("Admin seeding skipped or failed → %s", err)

        self.logger.info("Timeless Threads app initialized successfully.\n")
        return self.app
