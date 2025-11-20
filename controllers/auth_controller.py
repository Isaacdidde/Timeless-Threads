from flask import session, flash, redirect, url_for, render_template
from models.user_model import UserModel
from models.otp_model import OTP
from utils.otp_generator import otp_service
import datetime


class AuthController:
    def __init__(self, mongo):
        # Initialize database models
        self.users = UserModel(mongo)     # Handles user-related DB operations
        self.otps = OTP(mongo)            # Handles OTP-related DB operations
        self.mongo = mongo

    # ---------------------------------------------------------
    # LOGIN PAGE (simply returns template)
    # ---------------------------------------------------------
    def login_page(self):
        return render_template("login.html")

    # ---------------------------------------------------------
    # SEND LOGIN OTP
    # Triggered after user enters mobile number
    # ---------------------------------------------------------
    def send_login_otp(self, mobile):
        # Validate mobile number
        if not mobile:
            flash("Enter a valid mobile number!", "danger")
            return redirect(url_for("auth.login"))

        # Generate and send OTP
        otp = otp_service.generate_otp(mobile)

        # Store necessary session data for next steps
        session["otp_mobile"] = mobile
        session["otp_mode"] = "login"

        # Debug log (visible in terminal only)
        print("OTP (login) →", otp)

        flash("OTP sent successfully!", "success")
        return render_template("verify_otp.html", mobile=mobile)

    # ---------------------------------------------------------
    # VERIFY OTP
    # Common endpoint for both login and signup flows
    # ---------------------------------------------------------
    def verify_otp(self, mobile, otp_entered):
        mode = session.get("otp_mode")  # Detect which flow we’re in (login/signup)

        # Validate OTP correctness
        if not otp_service.verify_otp(mobile, otp_entered):
            flash("Invalid or expired OTP!", "danger")
            return redirect(url_for("auth.login"))

        # ---------------------- LOGIN FLOW ----------------------
        if mode == "login":
            user = self.users.find_by_mobile(mobile)

            if user:
                # Successful login
                session["user"] = user["name"]
                flash("Logged in successfully!", "success")
                return redirect(url_for("main.home"))
            else:
                # Mobile not registered → move to signup
                flash("Mobile number not registered!", "warning")
                return redirect(url_for("auth.signup_mobile"))

        # ---------------------- SIGNUP FLOW ----------------------
        if mode == "signup":
            return redirect(url_for("auth.complete_signup"))

        # Fallback in case session expired or tampered
        flash("Session expired. Please try again.", "warning")
        return redirect(url_for("auth.login"))

    # ---------------------------------------------------------
    # SIGNUP STEP 1 — Ask for mobile number
    # ---------------------------------------------------------
    def signup_mobile_page(self):
        return render_template("signup_mobile.html")

    # ---------------------------------------------------------
    # SIGNUP: VERIFY MOBILE NUMBER IS NOT ALREADY REGISTERED
    # ---------------------------------------------------------
    def verify_signup_mobile(self, mobile):
        # Check for empty input
        if not mobile:
            flash("Enter a valid mobile number!", "danger")
            return redirect(url_for("auth.signup_mobile"))

        # Prevent duplicate accounts
        if self.users.find_by_mobile(mobile):
            flash("Mobile already registered! Please login.", "warning")
            return redirect(url_for("auth.login"))

        # Store the mobile temporarily for next step
        session["pending_mobile"] = mobile
        return redirect(url_for("auth.signup_name"))

    # ---------------------------------------------------------
    # SIGNUP STEP 2 — Ask user to enter their name
    # ---------------------------------------------------------
    def signup_name_page(self):
        mobile = session.get("pending_mobile")

        # No mobile found → signup flow interrupted
        if not mobile:
            flash("Session expired. Try again.", "warning")
            return redirect(url_for("auth.signup_mobile"))

        return render_template("signup.html", mobile=mobile)

    # ---------------------------------------------------------
    # SIGNUP: SUBMIT NAME AND SEND OTP FOR ACCOUNT CREATION
    # ---------------------------------------------------------
    def submit_signup_name(self, name):
        mobile = session.get("pending_mobile")

        # Validate inputs
        if not name or not mobile:
            flash("Please enter your name.", "danger")
            return redirect(url_for("auth.signup_name"))

        # Store name in session for later account creation
        session["signup_name"] = name

        # Generate OTP for signup verification
        otp = otp_service.generate_otp(mobile)
        session["otp_mode"] = "signup"  # Switch OTP mode to signup flow

        print("OTP (signup) →", otp)  # Debug print

        flash("OTP sent! Please verify.", "success")
        return render_template("verify_otp.html", mobile=mobile)

    # ---------------------------------------------------------
    # SIGNUP FINAL STEP — Create user account
    # ---------------------------------------------------------
    def complete_signup(self):
        mobile = session.get("pending_mobile")
        name = session.get("signup_name")

        # If session data is missing, user probably refreshed or session expired
        if not mobile or not name:
            flash("Signup session expired!", "danger")
            return redirect(url_for("auth.signup_mobile"))

        # Insert new user in DB
        self.mongo.db.users.insert_one({
            "name": name,
            "mobile": mobile,
            "created_at": datetime.datetime.now()
        })

        # Log the user in immediately after account creation
        session["user"] = name

        # Clean up temporary session variables
        session.pop("pending_mobile", None)
        session.pop("signup_name", None)
        session.pop("otp_mode", None)

        flash("Account created successfully!", "success")
        return redirect(url_for("main.home"))

    # ---------------------------------------------------------
    # LOGOUT — Confirmation page
    # ---------------------------------------------------------
    def logout_page(self):
        # If user is not logged in, no point showing confirmation
        if "user" not in session:
            return redirect(url_for("main.home"))
        return render_template("logout_confirm.html")

    # ---------------------------------------------------------
    # LOGOUT — Clear session
    # ---------------------------------------------------------
    def logout_confirm(self):
        session.clear()  # Removes all session data
        flash("Logged out successfully!", "info")
        return redirect(url_for("main.home"))
