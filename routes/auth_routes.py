from flask import Blueprint, request
from database.connection import mongo
from controllers.auth_controller import AuthController

# ---------------------------------------------------------
# AUTH BLUEPRINT
# ---------------------------------------------------------
auth_bp = Blueprint("auth", __name__)
controller = AuthController(mongo)

# ---------------------------------------------------------
# LOGIN PAGE
# ---------------------------------------------------------
@auth_bp.route("/login")
def login():
    return controller.login_page()

# ---------------------------------------------------------
# SEND LOGIN OTP (EMAIL)
# ---------------------------------------------------------
@auth_bp.route("/send-login-email", methods=["POST"])
def send_login_email():
    email = request.form.get("email")
    return controller.send_login_email(email)

# ---------------------------------------------------------
# VERIFY LOGIN OTP
# ---------------------------------------------------------
@auth_bp.route("/verify-login-otp", methods=["POST"])
def verify_login_otp():
    email = request.form.get("email")
    otp = request.form.get("otp")
    return controller.verify_login_otp(email, otp)

# ---------------------------------------------------------
# SIGNUP STEP 1 — Email Input Page
# ---------------------------------------------------------
@auth_bp.route("/signup")
def signup_email_page():
    return controller.signup_email_page()

# ---------------------------------------------------------
# SIGNUP STEP 1 SUBMIT — Validate Email
# ---------------------------------------------------------
@auth_bp.route("/signup-verify-email", methods=["POST"])
def signup_verify_email():
    email = request.form.get("email")
    return controller.verify_signup_email(email)

# ---------------------------------------------------------
# SIGNUP STEP 2 — Enter Name Page
# ---------------------------------------------------------
@auth_bp.route("/signup-name")
def signup_name():
    return controller.signup_name_page()

# ---------------------------------------------------------
# SIGNUP STEP 2 SUBMIT — Save Name + Send OTP
# ---------------------------------------------------------
@auth_bp.route("/signup-submit-name", methods=["POST"])
def signup_submit_name():
    name = request.form.get("name")
    return controller.submit_signup_name(name)

# ---------------------------------------------------------
# VERIFY SIGNUP OTP
# ---------------------------------------------------------
@auth_bp.route("/verify-signup-otp", methods=["POST"])
def verify_signup_otp():
    email = request.form.get("email")
    otp = request.form.get("otp")
    return controller.verify_signup_otp(email, otp)

# ---------------------------------------------------------
# FINAL SIGNUP — Create Account
# ---------------------------------------------------------
@auth_bp.route("/complete-signup")
def complete_signup():
    return controller.complete_signup()

# ---------------------------------------------------------
# LOGOUT PAGES
# ---------------------------------------------------------
@auth_bp.route("/logout")
def logout_page():
    return controller.logout_page()

@auth_bp.route("/logout-confirm", methods=["POST"])
def logout_confirm():
    return controller.logout_confirm()
