import random
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from application.helpers.auth_helpers import check_password, create_user, generate_token
from application.models.db_tables import User
from application.database import db
from email.message import EmailMessage
import os
import smtplib

auth_bp = Blueprint("authentication", __name__)

login_manager = LoginManager()
login_manager.login_view = "authentication.login"


# ------------------- SMTP Email Helper -------------------
def send_email(to_email, message, subject):
    EMAIL_ADDRESS = os.getenv('SENDER_EMAIL')
    EMAIL_PASSWORD = os.getenv('SENDER_PASSWORD')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(message)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        print(f"OTP sent to {to_email}")


# ------------------- Flask-Login User Loader -------------------
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))


# ------------------- REGISTER -------------------
# @auth_bp.route("/register", methods=["GET", "POST"])
# def register():
#     step = request.form.get("step", "1")
#     message = None

#     if request.method == "POST":
#         # Step 1: Collect username/email/password
#         if step == "1":
#             username = request.form.get("username")
#             email = request.form.get("email")
#             password = request.form.get("password")

#             existing_user = db.session.query(User).filter_by(email=email).first()
#             if existing_user:
#                 if existing_user.is_email_verified:
#                     flash("Email already registered. Please login.", "info")
#                     return redirect(url_for("authentication.login"))
#                 else:
#                     # Resend OTP
#                     otp = existing_user.generate_otp(purpose="verify_email")
#                     send_email(email, f"Your OTP is {otp}. It expires in 10 minutes.", "Verify Email OTP")
#                     flash("OTP sent to your email.", "success")
#                     return render_template("register.html", step="2", email=email)

#             # Create new user
#             new_user = User(username=username, email=email)
#             new_user.set_password(password)  # assume you have a set_password method
#             db.session.add(new_user)
#             db.session.commit()

#             otp = new_user.generate_otp(purpose="verify_email")
#             send_email(email, f"Your OTP is {otp}. It expires in 10 minutes.", "Verify Email OTP")
#             flash("OTP sent to your email.", "success")
#             return render_template("register.html", step="2", email=email)

#         # Step 2: Verify OTP
#         elif step == "2":
#             email = request.form.get("email")
#             input_otp = request.form.get("otp")

#             user = db.session.query(User).filter_by(email=email).first()
#             if not user:
#                 flash("User not found. Please register again.", "danger")
#                 return redirect(url_for("authentication.register"))

#             is_verified, msg = user.verify_otp(input_otp, purpose="verify_email")
#             if not is_verified:
#                 flash(msg, "danger")
#                 return render_template("register.html", step="2", email=email)

#             user.is_email_verified = True
#             db.session.commit()
#             flash("Email verified! You can now login.", "success")
#             return redirect(url_for("authentication.login"))

#     return render_template("register.html", step="1", message=message)

# from application.helpers.auth_helpers import create_user, generate_token

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        user = create_user(username, email, password)

        token = generate_token(user, "email_verify")
        # send token.email here...
        flash("Account created! Verify your email.", "success")
        return redirect(url_for("authentication.login"))
    return render_template("register.html")


# ------------------- LOGIN -------------------


# For demo purposes, we'll store OTPs in memory
otp_store = {}

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    step = request.args.get("step")  # can be None, 'forgot_email', 'forgot_otp', 'forgot_reset'

    if request.method == "POST":
        # ----------------- Default login -----------------
        if step is None:
            email = request.form.get("email")
            password = request.form.get("password")
            # user = db.session.query(User).filter_by(email=email).first()

            user = db.session.query(User).filter_by(email=email).first()
            if not user or not check_password(user, password):
                flash("Invalid email or password", "danger")

            if not user or not user.check_password(password):
                flash("Invalid email or password.", "danger")
                return render_template("login.html", step=None, email=email)

            if not user.is_email_verified:
                flash("Please verify your email first.", "warning")
                return render_template("login.html", step=None, email=email)

            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("blog.index"))

        # --------------- Forgot Password: Enter Email -----------------
        elif step == "forgot_email":
            email = request.form.get("email")
            user = db.session.query(User).filter_by(email=email).first()

            if not user:
                flash("Email not found.", "danger")
                return render_template("login.html", step="forgot_email")

            # Generate a simple 6-digit OTP
            otp = str(random.randint(100000, 999999))
            otp_store[email] = otp  # Store OTP temporarily (replace with proper DB/email in real app)
            flash(f"OTP sent to your email (demo: {otp})", "info")
            return render_template("login.html", step="forgot_otp", email=email)

        # --------------- OTP Verification -----------------
        elif step == "forgot_otp":
            email = request.form.get("email")
            entered_otp = request.form.get("otp")

            if otp_store.get(email) != entered_otp:
                flash("Invalid OTP. Try again.", "danger")
                return render_template("login.html", step="forgot_otp", email=email)

            flash("OTP verified. You can reset your password now.", "success")
            return render_template("login.html", step="forgot_reset", email=email)

        # --------------- Reset Password -----------------
        elif step == "forgot_reset":
            email = request.form.get("email")
            password = request.form.get("password")
            user = db.session.query(User).filter_by(email=email).first()

            if not user:
                flash("Something went wrong. Try again.", "danger")
                return redirect(url_for("auth_bp.login"))

            user.set_password(password)  # Make sure your User model has set_password method
            db.session.commit()
            flash("Password reset successful! You can now login.", "success")
            otp_store.pop(email, None)
            return redirect(url_for("auth_bp.login"))

    # ---------------- GET requests -----------------
    return render_template("login.html", step=step)


# ------------------- LOGOUT -------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("blog.index"))

@auth_bp.route("/logout")
@login_required
def forgot_password():
    return f'Forgot password'