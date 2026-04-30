"""
Authentication routes replacing the Rust backend.

Provides:
  POST /api/init          - generate a short-lived API token (session seed)
  POST /api/create_user   - register a new user
  POST /api/login         - authenticate and return a JWT
"""

import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Header, HTTPException
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.db.mongo_client import db

router = APIRouter(prefix="/api")

# ── Security config ────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# ── Collections ────────────────────────────────────────────────────────────────
users_col = db["users"]
tokens_col = db["api_tokens"]


# ── Pydantic schemas ───────────────────────────────────────────────────────────
class UserCredentials(BaseModel):
    username: str
    password: str


# ── Helpers ────────────────────────────────────────────────────────────────────
def _create_jwt(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post("/init")
async def init():
    """
    Generate a short-lived API token used to authenticate create_user / login calls.
    Mirrors the Rust /api/init endpoint.
    """
    token = secrets.token_urlsafe(32)
    await tokens_col.insert_one({
        "token": token,
        "created_at": datetime.now(timezone.utc),
    })
    return {"api_token": token}


@router.post("/create_user")
async def create_user(
    credentials: UserCredentials,
    x_api_token: str = Header(..., alias="X-API-TOKEN"),
):
    """
    Register a new user. Requires a valid API token from /api/init.
    """
    # Validate API token
    valid = await tokens_col.find_one({"token": x_api_token})
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid API token")

    # Check duplicate username
    existing = await users_col.find_one({"username": credentials.username})
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    hashed = pwd_context.hash(credentials.password)
    await users_col.insert_one({
        "username": credentials.username,
        "password_hash": hashed,
        "created_at": datetime.now(timezone.utc),
    })
    return {"message": "User created successfully"}


@router.post("/login")
async def login(
    credentials: UserCredentials,
    x_api_token: str = Header(..., alias="X-API-TOKEN"),
):
    """
    Authenticate a user and return a JWT.
    Mirrors the Rust /api/login endpoint — returns {"jwt": "<token>"}.
    """
    # Validate API token
    valid = await tokens_col.find_one({"token": x_api_token})
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid API token")

    user = await users_col.find_one({"username": credentials.username})
    if not user or not pwd_context.verify(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    jwt_token = _create_jwt(credentials.username)
    return {"jwt": jwt_token}
