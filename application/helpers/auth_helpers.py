# application/helpers/auth_helpers.py
import bcrypt
import secrets
from datetime import datetime, timedelta
from ..models.db_tables import User, AuthToken
from ..database import db

# ---------------- Password Hashing ----------------
def hash_password(password: str) -> str:
    """Hash a plain text password."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def check_password(user: User, password: str) -> bool:
    """Check if the provided password matches the stored hash."""
    return bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8"))

# ---------------- User Creation ----------------
def create_user(username: str, email: str, password: str) -> User:
    """Create a new user with hashed password."""
    new_user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        is_email_verified=False
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user

# ---------------- Auth Token ----------------
def generate_token(user: User, token_type: str, expires_in_minutes: int = 30) -> AuthToken:
    """Generate a unique auth token (email_verify or password_reset)."""
    token = secrets.token_urlsafe(16)
    expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    auth_token = AuthToken(
        user_id=user.id,
        token=token,
        type=token_type,
        expires_at=expires_at
    )
    db.session.add(auth_token)
    db.session.commit()
    return auth_token

def verify_token(token_str: str, token_type: str) -> User | None:
    """Verify token and return the user if valid."""
    token = db.session.query(AuthToken).filter_by(
        token=token_str,
        type=token_type,
        is_used=False
    ).first()
    
    if token and token.expires_at > datetime.utcnow():
        token.is_used = True
        db.session.commit()
        return token.user
    return None

# ---------------- Password Reset ----------------
def reset_password(user: User, new_password: str):
    """Reset user's password."""
    user.password_hash = hash_password(new_password)
    db.session.commit()

# ---------------- OTP (Optional for stepwise login) ----------------
otp_store = {}

def generate_otp(email: str) -> str:
    """Generate a 6-digit OTP for email verification or password reset."""
    import random
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    return otp

def verify_otp(email: str, otp: str) -> bool:
    """Check if OTP matches."""
    if otp_store.get(email) == otp:
        otp_store.pop(email)
        return True
    return False
