from flask import session, flash, redirect, url_for, render_template
from models.user_model import UserModel
from models.otp_model import OTP
from utils.otp_generator import otp_service
import datetime
import requests
import os


class AuthController:
    def __init__(self, mongo):
        self.users = UserModel(mongo)
        self.otps = OTP(mongo)
        self.mongo = mongo

    # =====================================================================
    # SEND EMAIL USING RESEND API (SMTP BLOCKED ON RENDER)
    # =====================================================================
    def send_email(self, to_email, otp):
        api_key = os.getenv("RESEND_API_KEY")
        sender = os.getenv("EMAIL_FROM")

        if not api_key:
            print("❌ ERROR: RESEND_API_KEY missing in environment!")
            return False

        if not sender:
            print("❌ ERROR: EMAIL_FROM missing!")
            return False

        html_content = f"""
        <div style="font-family:Arial; max-width:420px; margin:auto; background:#fff;
                    padding:20px; border:1px solid #ddd; border-radius:10px;">

            <h2 style="text-align:center; margin-bottom:10px;">Timeless Threads</h2>

            <p style="font-size:15px; color:#444;">
                Use the OTP below to verify your identity. The code is valid for
                <strong>5 minutes</strong>.
            </p>

            <div style="text-align:center; margin:25px 0;">
                <div style="font-size:32px; font-weight:bold; letter-spacing:6px;">
                    {otp}
                </div>
            </div>

            <p style="font-size:14px; color:#666;">
                If you didn’t request this code, you may ignore this email.
            </p>

            <hr style="border:none; border-top:1px solid #ddd; margin:20px 0;">

            <p style="text-align:center; font-size:12px; color:#999;">
                © {datetime.datetime.now().year} Timeless Threads
            </p>
        </div>
        """

        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": sender,
            "to": to_email,
            "subject": "Your Timeless Threads OTP Code",
            "html": html_content
        }

        try:
            print("📨 Sending OTP via RESEND...")
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code in (200, 201):
                print("✔ OTP Email sent successfully through RESEND")
                return True
            else:
                print("❌ RESEND ERROR:", response.text)
                return False

        except Exception as e:
            print("❌ Email sending failed:", e)
            return False

    # =====================================================================
    # LOGIN PAGE
    # =====================================================================
    def login_page(self):
        return render_template("login.html")

    # =====================================================================
    # SEND LOGIN OTP
    # =====================================================================
    def send_login_email(self, email):
        if not email or "@" not in email:
            flash("Enter a valid email!", "danger")
            return redirect(url_for("auth.login"))

        otp = otp_service.generate_otp(email)

        session["otp_email"] = email
        session["otp_mode"] = "login"

        self.send_email(email, otp)

        flash("OTP sent to your email!", "success")
        return render_template("verify_otp.html", email=email)

    # =====================================================================
    # VERIFY LOGIN OTP
    # =====================================================================
    def verify_login_otp(self, email, otp_entered):
        if not otp_service.verify_otp(email, otp_entered):
            flash("Incorrect or expired OTP!", "danger")
            return redirect(url_for("auth.login"))

        user = self.users.find_by_email(email)

        if user:
            session["user"] = user["name"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.home"))

        flash("Email not registered. Please sign up.", "warning")
        return redirect(url_for("auth.signup_email_page"))

    # =====================================================================
    # SIGNUP EMAIL PAGE
    # =====================================================================
    def signup_email_page(self):
        return render_template("signup_mobile.html")

    # =====================================================================
    # VERIFY SIGNUP EMAIL
    # =====================================================================
    def verify_signup_email(self, email):
        if not email or "@" not in email:
            flash("Enter a valid email!", "danger")
            return redirect(url_for("auth.signup_email_page"))

        if self.users.find_by_email(email):
            flash("Email already registered!", "warning")
            return redirect(url_for("auth.login"))

        session["pending_email"] = email
        return redirect(url_for("auth.signup_name"))

    # =====================================================================
    # SIGNUP NAME PAGE
    # =====================================================================
    def signup_name_page(self):
        email = session.get("pending_email")

        if not email:
            flash("Session expired. Start again.", "warning")
            return redirect(url_for("auth.signup_email_page"))

        return render_template("signup.html", email=email)

    # =====================================================================
    # SUBMIT NAME + SEND OTP
    # =====================================================================
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

    # =====================================================================
    # VERIFY SIGNUP OTP
    # =====================================================================
    def verify_signup_otp(self, email, otp_entered):
        if not otp_service.verify_otp(email, otp_entered):
            flash("Invalid or expired OTP!", "danger")
            return redirect(url_for("auth.signup_email_page"))

        name = session.get("signup_name")

        if not name or not email:
            flash("Session expired.", "warning")
            return redirect(url_for("auth.signup_email_page"))

        self.users.create(email=email, extra={"name": name})
        session["user"] = name

        session.pop("signup_name", None)
        session.pop("pending_email", None)
        session.pop("otp_mode", None)

        flash("Account created successfully!", "success")
        return redirect(url_for("main.home"))

    # =====================================================================
    # LOGOUT PAGE
    # =====================================================================
    def logout_page(self):
        if "user" not in session:
            return redirect(url_for("main.home"))
        return render_template("logout_confirm.html")

    # =====================================================================
    # LOGOUT
    # =====================================================================
    def logout_confirm(self):
        session.clear()
        flash("Logged out successfully!", "info")
        return redirect(url_for("main.home"))
