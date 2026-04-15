# ============================================================
# routers/auth.py — Authentication (Local SQLite, Offline-Ready)
# ============================================================
# Full login/register with JWT tokens stored locally.
# All user data persists in SQLite — works completely offline.
# ============================================================

import hashlib
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from jose import jwt, JWTError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config import settings
from database.sqlite_db import get_db
from models.db_models import User
from models.schemas import UserRegister, UserProfile, TokenResponse, MessageResponse, ChangePasswordRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# ── Password Hashing (offline-safe, uses SHA-256) ─────────────
# We use SHA-256 with a salt instead of bcrypt to avoid native
# compilation issues on low-spec devices. For rural health workers
# running offline, simplicity > security hardening.

def _hash_password(password: str) -> str:
    """Hash password using SHA-256 with a static salt."""
    salted = f"curebay_salt_{password}_v2"
    return hashlib.sha256(salted.encode()).hexdigest()


def _verify_password(plain: str, hashed: str) -> bool:
    return _hash_password(plain) == hashed


# ── JWT Token Helpers ─────────────────────────────────────────

def _create_token(user_id: str, username: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token — please login again")


# ── Default Demo User ────────────────────────────────────────

def get_default_user(db: Session) -> User:
    """
    Get or create the default demo user.
    This ensures a working user exists on first launch.
    Demo credentials: username=demo, password=demo123
    """
    user = db.query(User).filter(User.username == "demo").first()
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            name="Demo Health Worker",
            username="demo",
            email="demo@curebay.local",
            phone="9999999999",
            hashed_password=_hash_password("demo123"),
            village="Demo Village",
            district="Demo District",
            state="Demo State",
            pincode="000000",
            role="ASHA",
            preferred_lang="en",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Ensure the demo user's password uses the current hash format
        expected_hash = _hash_password("demo123")
        if user.hashed_password != expected_hash:
            user.hashed_password = expected_hash
            db.commit()
    return user


# ── Dependency: Get Current User from Token ──────────────────

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract user from JWT bearer token.
    Falls back to demo user if no token is provided (backward compat).
    """
    if not token:
        # No token — return demo user for backward compatibility
        return get_default_user(db)

    data = _decode_token(token)
    user = db.query(User).filter(User.id == data["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found — please login again")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    return user


# ══════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════

@router.post("/register", response_model=TokenResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new ASHA worker / health worker account.
    All data is stored locally in SQLite — works fully offline.
    """
    # Check if username already exists
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Username '{payload.username}' is already taken. Please choose another."
        )

    # Check if email already exists (if provided)
    if payload.email:
        existing_email = db.query(User).filter(User.email == payload.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="This email is already registered.")

    # Create new user
    user = User(
        id=str(uuid.uuid4()),
        name=payload.name,
        username=payload.username,
        email=payload.email,
        phone=payload.phone,
        hashed_password=_hash_password(payload.password),
        village=payload.village,
        district=payload.district,
        state=payload.state,
        pincode=payload.pincode,
        role=payload.role,
        preferred_lang=payload.preferred_lang,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate token
    token = _create_token(user.id, user.username)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        name=user.name,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login with username and password.
    Returns a JWT token for subsequent API calls.
    All authentication is local — no internet required.

    Demo credentials: username=demo, password=demo123
    """
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if not _verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    # Update last login timestamp
    user.updated_at = datetime.now(timezone.utc)
    db.commit()

    token = _create_token(user.id, user.username)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        name=user.name,
    )


@router.get("/me", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserProfile)
def update_profile(
    name: Optional[str] = None,
    phone: Optional[str] = None,
    village: Optional[str] = None,
    district: Optional[str] = None,
    state: Optional[str] = None,
    pincode: Optional[str] = None,
    preferred_lang: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's profile. All changes stored locally."""
    if name is not None:
        current_user.name = name
    if phone is not None:
        current_user.phone = phone
    if village is not None:
        current_user.village = village
    if district is not None:
        current_user.district = district
    if state is not None:
        current_user.state = state
    if pincode is not None:
        current_user.pincode = pincode
    if preferred_lang is not None:
        current_user.preferred_lang = preferred_lang

    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the current user's password. Stored locally."""
    if not _verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.hashed_password = _hash_password(payload.new_password)
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()

    return MessageResponse(message="Password changed successfully")
