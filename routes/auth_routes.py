from flask import Blueprint, request
from database.connection import mongo
from controllers.auth_controller import AuthController

# ---------------------------------------------------------
# AUTH BLUEPRINT
#
# This blueprint groups all authentication-related routes:
#   - Login (OTP-based)
#   - Signup (multi-step: mobile → name → verify OTP → create account)
#   - Logout
#
# The AuthController handles all the business logic.
# ---------------------------------------------------------
auth_bp = Blueprint("auth", __name__)
controller = AuthController(mongo)


# ---------------------------------------------------------
# LOGIN PAGE (GET)
#
# Renders the login form where user enters mobile number.
# ---------------------------------------------------------
@auth_bp.route("/login")
def login():
    return controller.login_page()


# ---------------------------------------------------------
# SEND LOGIN OTP (POST)
#
# Receives mobile number from form and sends OTP.
# Redirects to OTP verification page.
# ---------------------------------------------------------
@auth_bp.route("/send-otp", methods=["POST"])
def send_otp():
    mobile = request.form.get("mobile")
    return controller.send_login_otp(mobile)


# ---------------------------------------------------------
# VERIFY OTP (POST)
#
# Called after user submits OTP during login/signup.
# Controller determines whether this is login or signup mode.
# ---------------------------------------------------------
@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    mobile = request.form.get("mobile")
    otp = request.form.get("otp")
    return controller.verify_otp(mobile, otp)


# ---------------------------------------------------------
# SIGNUP FLOW — STEP 1
#
# Display mobile input for signup.
# ---------------------------------------------------------
@auth_bp.route("/signup")
def signup_mobile():
    return controller.signup_mobile_page()


# ---------------------------------------------------------
# SIGNUP FLOW — STEP 1 SUBMISSION
#
# Validates mobile, checks duplicates, then moves to name step.
# ---------------------------------------------------------
@auth_bp.route("/signup-verify-mobile", methods=["POST"])
def signup_verify_mobile():
    mobile = request.form.get("mobile")
    return controller.verify_signup_mobile(mobile)


# ---------------------------------------------------------
# SIGNUP FLOW — STEP 2
#
# User enters their name after mobile verification.
# ---------------------------------------------------------
@auth_bp.route("/signup-name")
def signup_name():
    return controller.signup_name_page()


# ---------------------------------------------------------
# SIGNUP FLOW — STEP 2 SUBMISSION
#
# Submits the name and triggers OTP for signup verification.
# ---------------------------------------------------------
@auth_bp.route("/signup-submit-name", methods=["POST"])
def signup_submit_name():
    name = request.form.get("name")
    return controller.submit_signup_name(name)


# ---------------------------------------------------------
# FINAL ACCOUNT CREATION (GET)
#
# Runs only after OTP verification.
# Creates the user and logs them in automatically.
# ---------------------------------------------------------
@auth_bp.route("/complete-signup")
def complete_signup():
    return controller.complete_signup()


# ---------------------------------------------------------
# LOGOUT — CONFIRMATION PAGE (GET)
#
# Asks user to confirm logout.
# ---------------------------------------------------------
@auth_bp.route("/logout")
def logout_page():
    return controller.logout_page()


# ---------------------------------------------------------
# LOGOUT — FINAL ACTION (POST)
#
# Clears session and logs out user.
# ---------------------------------------------------------
@auth_bp.route("/logout-confirm", methods=["POST"])
def logout_confirm():
    return controller.logout_confirm()
