from email.message import EmailMessage
import os
import smtplib
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from application.models.db_tables import User
from application.database import db

auth_bp = Blueprint("authentication", __name__)

# ------------------------------------------

# SMTP HANDLER
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
        print(f"OTP is send to {to_email}")

# -----------------------------------------------------------------------------------

# ================= REGISTER =================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    message = None

    # Default to step 1
    step = session.get('step', 1)

    if request.method == 'POST':
        step = int(request.form.get('step', 1))

        if step == 1:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            if db.email_exists(email):
                verified = db.is_verified(email)
                if not verified:
                    user = db.get_user_by_email(email)
                    otp = db.generate_otp(user['id'], purpose='verify_email')
                    send_email(email, f"Your OTP is {otp}. It expires in 10 minutes.", "Email Verification OTP")
                    session['email'] = email
                    session['step'] = 2
                    flash('OTP sent to your registered email.', 'success')
                    return redirect(url_for('register'))
                else:
                    flash("User already registered and verified. Please login.", "info")
                    return redirect(url_for('login'))

            else:
                success, result = db.register_user(username, email, password)
                if success:
                    user = db.get_user_by_email(email)
                    otp = db.generate_otp(user['id'], purpose='verify_email')
                    send_email(email, f"Your OTP is {otp}. It expires in 10 minutes.", "User Registration OTP")
                    session['email'] = email
                    session['step'] = 2
                    flash('OTP sent to your registered email.', 'success')
                    return redirect(url_for('register'))
                else:
                    message = result

        elif step == 2:
            email = session.get('email')
            if not email:
                flash("Session expired. Please start again.", "danger")
                return redirect(url_for('register'))

            user = db.get_user_by_email(email)
            action = request.form.get('action', 'verify')

            if action == 'resend':
                otp = db.generate_otp(user['id'], purpose='verify_email')
                send_email(email, f"Your new OTP is {otp}", "Resend OTP")
                flash("OTP resent to your email.", "success")
                session['step'] = 2
                return redirect(url_for('register'))

            elif action == 'verify':
                input_otp = request.form.get('otp')
                is_verified, message = db.verify_otp(user['id'], input_otp, purpose='verify_email')
                if not is_verified:
                    flash(message, "danger")
                    session['step'] = 2
                    return redirect(url_for('register'))

                db.mark_user_verified(user['id'])
                session.pop('email', None)
                session.pop('step', None)
                flash("Email verified successfully. Please login.", "success")
                return redirect(url_for('login'))

    return render_template('register.html', step=step, message=message)


@auth_bp.route('/register/back')
def register_back():
    session['step'] = 1
    return redirect(url_for('register'))

# ================= LOGIN =================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    step = session.get('step')  # None, forgot_email, forgot_otp, forgot_reset

    # -------------------- GET --------------------
    if request.method == 'GET':
        # User clicked "Forgot password?"
        if request.args.get('forgot') == '1':
            session['step'] = 'forgot_email'
            step = 'forgot_email'

        return render_template('login.html', step=step)

    # -------------------- POST --------------------

    # ========== NORMAL LOGIN ==========
    if step is None:
        email = request.form.get('email')
        password = request.form.get('password')

        success, result = db.login_user(email, password)

        if not success:
            flash(result, "danger")
            return render_template('login.html', step=None)

        # Login success
        session.clear()
        session['user_id'] = result['id']
        session['username'] = result['username']
        session['email'] = result['email']
        session['user_role'] = result['role']

        flash("Login successful 🎉", "success")
        return redirect(url_for('dashboard'))

    # ========== FORGOT PASSWORD : EMAIL ==========
    elif step == 'forgot_email':
        email = request.form.get('email')

        user = db.get_user_by_email(email)
        if not user:
            flash("Email not registered", "danger")
            return redirect(url_for('login'))

        # Save reset info
        session['reset_user_id'] = user['id']
        session['reset_email'] = user['email']

        otp = db.generate_otp(user['id'], purpose='reset_password')


        subject = "Password Reset OTP"
        message = f"Your OTP is {otp}. It expires in 10 minutes."
        send_email(email, message, subject)

        session['step'] = 'forgot_otp'
        flash("OTP sent to your email", "success")
        return redirect(url_for('login'))

    # ========== FORGOT PASSWORD : OTP ==========
    elif step == 'forgot_otp':
        user_otp = request.form.get('otp')

        user_id = session.get('reset_user_id')
        if not user_id:
            flash("Session expired. Please try again.", "danger")
            session.pop('step', None)
            return redirect(url_for('login'))


        is_verified, message = db.verify_otp(
            user_id=session['reset_user_id'],
            input_otp=user_otp,
            purpose='reset_password'
        )

        
        if not is_verified:
            flash(message, "danger")
            session['step'] = 'forgot_otp'
            return redirect(url_for('login'))


        session['step'] = 'forgot_reset'
        flash("OTP verified successfully", "success")
        return redirect(url_for('login'))

    # ========== FORGOT PASSWORD : RESET ==========
    elif step == 'forgot_reset':
        password = request.form.get('password')
        email = session.get('reset_email')

        success, message = db.update_user_password(email, password)

        # Clear reset session
        session.pop('reset_user_id', None)
        session.pop('reset_email', None)
        session.pop('step', None)

        flash("Password reset successful. Please login.", "success")
        return redirect(url_for('login'))

# ================= LOGOUT =================
@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('username', None)
    session.pop('email', None)
    flash('Logout successfully!', 'success')
    return redirect(url_for('home'))
