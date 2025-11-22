from flask import session, flash, redirect, url_for, render_template
from models.user_model import UserModel
from models.otp_model import OTP
from utils.otp_generator import otp_service
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


class AuthController:
    def __init__(self, mongo):
        self.users = UserModel(mongo)
        self.otps = OTP(mongo)
        self.mongo = mongo

    # ---------------------------------------------------------
    # SEND EMAIL (Professional HTML OTP Email)
    # ---------------------------------------------------------
    def send_email(self, to_email, otp):
        smtp_host = os.getenv("EMAIL_HOST")
        smtp_port = int(os.getenv("EMAIL_PORT"))
        smtp_user = os.getenv("EMAIL_USER")
        smtp_pass = os.getenv("EMAIL_PASS")

        # Beautiful HTML email
        html_content = f"""
        <div style="font-family:Arial; max-width:420px; margin:auto; background:#fff; padding:20px; border:1px solid #ddd; border-radius:10px;">
            <h2 style="text-align:center; color:#000; margin-bottom:10px;">
                Timeless Threads
            </h2>

            <p style="font-size:15px; color:#444;">
                Use the OTP below to verify your identity. This code is valid for 
                <strong>5 minutes</strong>.
            </p>

            <div style="text-align:center; margin:25px 0;">
                <div style="font-size:32px; font-weight:bold; letter-spacing:6px; color:#222;">
                    {otp}
                </div>
            </div>

            <p style="font-size:14px; color:#666;">
                If you did not request this code, you may safely ignore this email.
            </p>

            <hr style="border:none; border-top:1px solid #ddd; margin:20px 0;">

            <p style="text-align:center; font-size:12px; color:#999;">
                © {datetime.datetime.now().year} Timeless Threads • All rights reserved.
            </p>
        </div>
        """

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Your Timeless Threads OTP Code"
            msg["From"] = smtp_user
            msg["To"] = to_email
            msg.attach(MIMEText(html_content, "html"))

            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
            server.quit()

            print("📩 OTP email sent successfully")
            return True

        except Exception as e:
            print("❌ Email sending failed:", e)
            return False

    # ---------------------------------------------------------
    # LOGIN PAGE
    # ---------------------------------------------------------
    def login_page(self):
        return render_template("login.html")

    # ---------------------------------------------------------
    # SEND LOGIN OTP
    # ---------------------------------------------------------
    def send_login_email(self, email):
        if not email or "@" not in email:
            flash("Enter a valid email address!", "danger")
            return redirect(url_for("auth.login"))

        otp = otp_service.generate_otp(email)

        session["otp_email"] = email
        session["otp_mode"] = "login"

        self.send_email(email, otp)

        flash("OTP has been sent to your email!", "success")
        return render_template("verify_otp.html", email=email)

    # ---------------------------------------------------------
    # VERIFY LOGIN OTP
    # ---------------------------------------------------------
    def verify_login_otp(self, email, otp_entered):
        if not otp_service.verify_otp(email, otp_entered):
            flash("Incorrect or expired OTP!", "danger")
            return redirect(url_for("auth.login"))

        user = self.users.find_by_email(email)

        if user:
            session["user"] = user["name"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.home"))

        flash("Email not registered. Please create an account.", "warning")
        return redirect(url_for("auth.signup_email_page"))

    # ---------------------------------------------------------
    # SIGNUP EMAIL PAGE
    # ---------------------------------------------------------
    def signup_email_page(self):
        return render_template("signup_mobile.html")

    # ---------------------------------------------------------
    # VERIFY EMAIL NOT REGISTERED
    # ---------------------------------------------------------
    def verify_signup_email(self, email):
        if not email or "@" not in email:
            flash("Enter a valid email address!", "danger")
            return redirect(url_for("auth.signup_email_page"))

        if self.users.find_by_email(email):
            flash("Email already registered! Please login.", "warning")
            return redirect(url_for("auth.login"))

        session["pending_email"] = email
        return redirect(url_for("auth.signup_name"))

    # ---------------------------------------------------------
    # SIGNUP NAME PAGE
    # ---------------------------------------------------------
    def signup_name_page(self):
        email = session.get("pending_email")

        if not email:
            flash("Session expired. Start signup again.", "warning")
            return redirect(url_for("auth.signup_email_page"))

        return render_template("signup.html", email=email)

    # ---------------------------------------------------------
    # SUBMIT NAME + SEND OTP
    # ---------------------------------------------------------
    def submit_signup_name(self, name):
        email = session.get("pending_email")

        if not name or not email:
            flash("Please enter your name.", "danger")
            return redirect(url_for("auth.signup_name"))

        session["signup_name"] = name

        otp = otp_service.generate_otp(email)
        session["otp_mode"] = "signup"

        self.send_email(email, otp)

        flash("OTP sent to your email!", "success")
        return render_template("verify_otp.html", email=email)

    # ---------------------------------------------------------
    # VERIFY SIGNUP OTP
    # ---------------------------------------------------------
    def verify_signup_otp(self, email, otp_entered):
        if not otp_service.verify_otp(email, otp_entered):
            flash("Invalid or expired OTP!", "danger")
            return redirect(url_for("auth.signup_email_page"))

        name = session.get("signup_name")

        if not name or not email:
            flash("Session expired. Please try again.", "warning")
            return redirect(url_for("auth.signup_email_page"))

        # Create user
        self.users.create(email=email, extra={"name": name})

        session["user"] = name

        # Clean session
        session.pop("signup_name", None)
        session.pop("pending_email", None)
        session.pop("otp_mode", None)

        flash("Account created successfully!", "success")
        return redirect(url_for("main.home"))

    # ---------------------------------------------------------
    # LOGOUT PAGE
    # ---------------------------------------------------------
    def logout_page(self):
        if "user" not in session:
            return redirect(url_for("main.home"))
        return render_template("logout_confirm.html")

    # ---------------------------------------------------------
    # LOGOUT ACTION
    # ---------------------------------------------------------
    def logout_confirm(self):
        session.clear()
        flash("Logged out successfully!", "info")
        return redirect(url_for("main.home"))
