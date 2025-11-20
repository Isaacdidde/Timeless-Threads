import os
from flask import Flask
from config import DevelopmentConfig
from database.connection import init_db


class AppFactory:
    """
    Factory class responsible for creating and configuring the Flask application.

    Responsibilities:
    ▸ Load environment + instance configuration
    ▸ Initialize extensions (MongoDB, etc.)
    ▸ Configure Jinja templating environment
    ▸ Register blueprints only AFTER DB setup
    """

    def __init__(self, config_class=DevelopmentConfig):
        # Store config class (DevelopmentConfig by default)
        self.config_class = config_class

        # Create Flask application object
        # instance_relative_config=True → keeps instance/ folder for secrets
        self.app = Flask(__name__, instance_relative_config=True)

    # ------------------------------------------------------
    # CONFIGURATION LOADER
    # ------------------------------------------------------
    def load_config(self):
        """
        Load base configuration, then apply optional instance-level overrides.
        """

        # Load base config from the selected config class
        self.app.config.from_object(self.config_class)

        # Path: instance/config.py → usually for secrets on production
        instance_config_path = os.path.join(self.app.instance_path, "config.py")

        # Load instance config only if it exists
        if os.path.exists(instance_config_path):
            try:
                self.app.config.from_pyfile("config.py")
            except Exception:
                # Silently ignore malformed instance config files
                pass

        # Ensure "instance/" directory exists
        os.makedirs(self.app.instance_path, exist_ok=True)

    # ------------------------------------------------------
    # INITIALIZE EXTENSIONS (Mongo, etc.)
    # ------------------------------------------------------
    def init_extensions(self):
        """
        Initialize required extensions before routes are imported.

        MongoDB must be set up BEFORE route imports, because controllers
        will require an active connection.
        """
        init_db(self.app)

    # ------------------------------------------------------
    # JINJA TEMPLATE SETTINGS
    # ------------------------------------------------------
    def init_jinja(self):
        """
        Make Jinja templates cleaner by trimming whitespace.
        """
        self.app.jinja_env.trim_blocks = True
        self.app.jinja_env.lstrip_blocks = True

    # ------------------------------------------------------
    # REGISTER BLUEPRINTS
    # ------------------------------------------------------
    def init_blueprints(self):
        """
        Import and register all application blueprints.
        This must be done *after* Mongo initialization.
        """
        from routes import register_blueprints
        register_blueprints(self.app)

    # ------------------------------------------------------
    # CREATE APP INSTANCE
    # ------------------------------------------------------
    def create_app(self):
        """
        The main factory method.
        Called from run.py or gunicorn to build the Flask app.
        """

        self.load_config()       # Load base + instance config
        self.init_extensions()   # Initialize MongoDB & other extensions
        self.init_jinja()        # Improve Jinja environment
        self.init_blueprints()   # Import and attach all route blueprints

        return self.app          # Return the fully prepared Flask app
