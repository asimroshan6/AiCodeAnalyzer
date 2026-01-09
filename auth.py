from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models import User
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Optional
from database import Session
from config import settings


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

auth2_bearer = OAuth2PasswordBearer(tokenUrl="/user/login/")


def hash_password(password: str) -> str:
    hashed_password = bcrypt_context.hash(password)
    return hashed_password


def create_access_token(username: str, user_id: int, expires_delta: timedelta) -> str:
    payload = {'username': username, 'user_id': user_id, 'exp': datetime.now(timezone.utc) + expires_delta}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return token


def verify_user(username: str, password: str, db: Session) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    
    return user
    

def get_current_user(token: str = Depends(auth2_bearer)) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM, ])
        username = payload.get('username')
        user_id = payload.get('user_id')
        
        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return {'username': username, 'user_id': user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
