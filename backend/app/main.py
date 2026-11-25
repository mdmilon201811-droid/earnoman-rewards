"""Starter authentication API for EarnWorld Rewards.

Development-ready foundation only. Configure PostgreSQL, HTTPS, email verification,
password reset, rate limiting, monitoring and legal notices before public launch.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Generator

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash
from sqlalchemy import Boolean, DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

APP_ENV = os.getenv("APP_ENV", "development")
SECRET = os.getenv("JWT_SECRET_KEY", "")
if APP_ENV == "production" and (len(SECRET) < 32 or SECRET.startswith("CHANGE-ME")):
    raise RuntimeError("Set a strong JWT_SECRET_KEY (at least 32 characters) in production.")
if not SECRET:
    SECRET = "local-development-only-secret-change-before-deploy-000000"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)
password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)
app = FastAPI(title=f"{os.getenv('APP_NAME', 'EarnWorld Rewards')} Auth API", version="0.1.0")

class RegisterInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class PublicUser(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: PublicUser

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def issue_token(user: User) -> TokenOutput:
    minutes = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
    expires = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    token = jwt.encode({"sub": str(user.id), "exp": expires, "iat": datetime.now(timezone.utc)}, SECRET, algorithm="HS256")
    return TokenOutput(access_token=token, expires_in=minutes * 60, user=PublicUser(id=user.id, email=user.email, is_active=user.is_active))

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(credentials.credentials, SECRET, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Account unavailable")
    return user

@app.get("/health")
def health():
    return {"status": "ok", "service": "EarnWorld Rewards authentication", "environment": APP_ENV, "production_ready": False}

@app.post("/auth/register", response_model=TokenOutput, status_code=201)
def register(payload: RegisterInput, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(email=email, password_hash=password_hash.hash(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return issue_token(user)

@app.post("/auth/login", response_model=TokenOutput)
def login(payload: LoginInput, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not password_hash.verify(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    return issue_token(user)

@app.get("/auth/me", response_model=PublicUser)
def me(user: User = Depends(current_user)):
    return PublicUser(id=user.id, email=user.email, is_active=user.is_active)
