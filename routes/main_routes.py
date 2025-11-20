from flask import Blueprint, request
from database.connection import mongo
from controllers.main_controller import MainController

# ---------------------------------------------------------
# MAIN BLUEPRINT
#
# Handles general site pages:
#   - Homepage
#   - Search
#   - FAQ
#   - Contact
#   - Policies
#
# All business logic is delegated to MainController.
# ---------------------------------------------------------
main_bp = Blueprint("main", __name__)

# Initialize the controller with MongoDB connection
controller = MainController(mongo)


# ---------------------------------------------------------
# HOMEPAGE
#
# Loads featured products (limit handled in controller).
# URL: GET /
# ---------------------------------------------------------
@main_bp.route("/")
def home():
    return controller.home()


# ---------------------------------------------------------
# SEARCH
#
# Reads query from URL parameter:
#     /search?q=shirt
#
# Strips whitespace and forwards it to the controller.
# If query is empty, controller returns empty results.
# ---------------------------------------------------------
@main_bp.route("/search")
def search():
    query = request.args.get("q", "").strip()
    return controller.search(query)


# ---------------------------------------------------------
# FAQ PAGE
#
# Renders static FAQ information.
# URL: GET /faq
# ---------------------------------------------------------
@main_bp.route("/faq")
def faq():
    return controller.faq()


# ---------------------------------------------------------
# CONTACT PAGE
#
# Displays contact form or company contact details.
# URL: GET /contact
# ---------------------------------------------------------
@main_bp.route("/contact")
def contact():
    return controller.contact()


# ---------------------------------------------------------
# POLICIES PAGE
#
# Shows privacy policy, return policy, shipping rules, etc.
# URL: GET /policies
# ---------------------------------------------------------
@main_bp.route("/policies")
def policies():
    return controller.policies()
