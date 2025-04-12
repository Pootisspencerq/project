from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models import User
from database import get_db
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets

SECRET_KEY = "secretkey"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_salt():
    return secrets.token_hex(8)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed_with_salt: str):
    hashed, salt = hashed_with_salt.split(':')
    return pwd_context.verify(password + salt, hashed)

def authenticate_user(db: Session, login: str, password: str):
    user = db.query(User).filter(User.login == login).first()
    if not user or not verify_password(password, user.password):
        return None
    return user

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login = payload.get("sub")
        user = db.query(User).filter(User.login == login).first()
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
