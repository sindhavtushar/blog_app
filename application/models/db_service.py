# application/mdodels/db_service.py


from application.database import db
from application.models.db_tables import Category, User


from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime, timedelta


def email_exists(email):
    [query]("SELECT 1 FROM users WHERE email = %s", (email,))
    return  is not None

def get_user_by_email(email):
    [query]("""
        SELECT id, username, email
        FROM users
        WHERE email = %s
    """, (email,))
    return 

def get_user_id(email):
    [query]("SELECT id FROM users WHERE email = %s", (email,))
    row = 
    return row['id'] if row else None

def is_verified(email):
    [query]("SELECT is_verified FROM users WHERE email = %s", (email,))
    row = 
    return row['is_verified'] if row else None

def insert_user(username, email, password, role='user'):
    hashed_pw = generate_password_hash(password)
    try:
        [query]("""
            INSERT INTO users (username, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            RETURNING id, username, email, role, is_verified
        """, (username, email, hashed_pw, role))
        conn.commit()
        return 
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return None

def get_users_by_role(role, requester_role):
    """
    Fetch users filtered by role, only if requester is admin or senior.
    
    :param role: Role to filter ('admin', 'senior', 'user')
    :param requester_role: Role of the user making the request
    :return: List of users matching the role
    """
    if requester_role not in ('admin', 'senior'):
        return []  # Only admin or senior can fetch users

    [query]("""
        SELECT id, username, email, role, is_verified, created_at
        FROM users
        WHERE role = %s
        ORDER BY username
    """, (role,))
    
    return all()

def mark_user_verified(user_id):
        """
        Mark a user as verified.
        """
        try:
            query = "UPDATE users SET is_verified = TRUE WHERE id = %s"
            [query](query, (user_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[DB ERROR] mark_user_verified: {e}")
            return False

def register_user(username, email, password):
    if email_exists(email):
        return False, "Email already registered"

    user = insert_user(username, email, password)
    if user:
        return True, user
    return False, "Registration failed"

def login_user(email, password):
    [query]("""
        SELECT id, username, email, password_hash, role, is_verified
        FROM users
        WHERE email = %s
    """, (email,))
    user = 
    if not user:
        return False, "User not found"
    if not user["is_verified"]:
        return False, "Account not verified"
    if not check_password_hash(user["password_hash"], password):
        return False, "Invalid password"
    return True, {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"]
    }

def update_user_password(email, password):
    hashed_password = generate_password_hash(password)

    try:
        [query]("""
            UPDATE users
            SET password_hash = %s
            WHERE email = %s;
        """, (hashed_password, email))

        conn.commit()  # ✅ VERY IMPORTANT

        if cursor.rowcount == 0:
            return False, "User not found"

        return True, "Password updated successfully"

    except psycopg2.Error as e:
        conn.rollback()
        return False, f"Database error: {e}"

    except Exception as e:
        conn.rollback()
        return False, f"Unexpected error: {e}"


# OTP HELPERS

def generate_otp(user_id, purpose='verify_email', expiry_minutes=10):
    # otp = ''.join(random.choices(string.digits, k=6))
    # otp_hash = generate_password_hash(otp)

    otp = str(random.randint(100000, 999999))
    otp_hash = generate_password_hash(otp)

    expires_at = datetime.now() + timedelta(minutes=expiry_minutes)

    [query]("""
        INSERT INTO user_otp (user_id, otp_hash, purpose, expires_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (user_id, otp_hash, purpose, expires_at))
    conn.commit()
    return otp  # Send this to user via email/SMS

def verify_otp(user_id, input_otp, purpose='verify_email'):
    input_otp = str(input_otp).strip()
    [query]("""
        SELECT id, otp_hash, expires_at, is_used
        FROM user_otp
        WHERE user_id = %s AND purpose = %s AND is_used = FALSE
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id, purpose))
    row = 
    if not row:
        return False, "No OTP found"
    if datetime.now() > row['expires_at']:
        return False, "OTP expired"
    if not check_password_hash(row['otp_hash'], input_otp):
        return False, "Invalid OTP"

    # Mark OTP used
    [query]("UPDATE user_otp SET is_used = TRUE WHERE id = %s", (row['id'],))
    conn.commit()
    if purpose == 'verify_email':
        [query](
            "UPDATE users SET is_verified = TRUE WHERE id = %s",
            (user_id,)
        )
        conn.commit()
    return True, "OTP verified"


# ADMIN / SENIOR HELPERS

def create_admin(username, email, password):
    return insert_user(username, email, password, role='admin')

def create_senior(username, email, password):
    return insert_user(username, email, password, role='senior')

def list_users(requester_role):
    if requester_role not in ('admin', 'senior'):
        return []
    [query]("""
        SELECT id, username, email, role, is_verified, created_at
        FROM users
        ORDER BY role DESC, username
    """)
    return all()


# User operations ----------------------------------------------------------------------------------

# check user exists or not
# get user by email
# delete specific user (Admin only)
# update_user

# Authentication Functionalities ---------------------------------------------------------------------

# register user
# login user
# reset password
# verify user

# Blog functionalities 

# add blog
# update blog
# delete blog





def create_user(username, email, password_hash, is_admin=False):
    try:
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            is_admin=is_admin
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {e}")
        return None
    



