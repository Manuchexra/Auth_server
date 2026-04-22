from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from core.config import config

pwd_context = CryptContext(schemes = ["argon2"], deprecated = "auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject:str , expires_delta: Optional[timedelta] = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + config.access_token_expire_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

    return encoded_jwt


def create_refresh_token(subject:str, expires_delta: Optional[timedelta] = None):
    if expires_delta is None:
        expire = timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(subject, expires_delta)


def decode_token(token: str) -> dict:
    payload = jwt.decode(token, config.SECRET_KEY, algorithms= [config.ALGORITHM])
    return payload


