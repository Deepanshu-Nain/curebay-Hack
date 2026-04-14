# ============================================================
# routers/auth.py — Authentication & User Management
# ============================================================

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import settings
from database.sqlite_db import get_db
from models.db_models import User
from models.schemas import (
    UserRegister, TokenResponse, UserProfile, MessageResponse, ChangePasswordRequest
)

router = APIRouter(prefix="/auth", tags=["Authentication (Login Required)"])

# ── Password hashing ──────────────────────────────────────────
# Using bcrypt directly for better compatibility with newer versions
import bcrypt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    # bcrypt expects bytes and returns bytes, decode to string for DB storage
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against hash."""
    password_bytes = plain.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ── JWT ───────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


# ── Endpoints ─────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new health worker account.

    After registration, you'll receive a JWT token automatically.
    Use this token to authenticate other endpoints.

    **Required fields:**
    - `username`: Unique username
    - `password`: At least 6 characters
    - `name`: Full name
    - `role`: ASHA, ANM, MO, or Other

    **Optional fields:** email, phone, village, district, state, pincode, preferred_lang
    """
    # Check unique username
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(400, detail="Username already taken.")
    if payload.email and db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(400, detail="Email already registered.")

    user = User(
        name=payload.name,
        username=payload.username,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        village=payload.village,
        district=payload.district,
        state=payload.state,
        pincode=payload.pincode,
        role=payload.role,
        preferred_lang=payload.preferred_lang,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(access_token=token, user_id=user.id, name=user.name)


@router.post("/login", response_model=TokenResponse, summary="Login - Get JWT Token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login with username and password to get a JWT access token.

    **How to use in Swagger UI:**
    1. Use the demo account: username=`demo`, password=`demo123`
    2. Or register first using POST /auth/register
    3. Copy the `access_token` from response
    4. Click 'Authorize' button at top and enter: `Bearer <your_token>`

    **For programmatic use:** Send form data with `username` and `password` fields.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
    if not user.is_active:
        raise HTTPException(403, detail="Account is disabled.")

    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(access_token=token, user_id=user.id, name=user.name)


@router.get("/me", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserProfile)
def update_profile(
    updates: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update profile fields (name, phone, village, language, etc.)."""
    allowed = {"name", "phone", "village", "district", "state", "pincode", "preferred_lang"}
    for field, value in updates.items():
        if field in allowed:
            setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change password for the current user."""
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(400, detail="Old password is incorrect.")
    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return MessageResponse(message="Password updated successfully.")
