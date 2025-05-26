# app/api/user.py: User API endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models import repository, db
from app.schemas import user as user_schema
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import passlib.hash as _hash
import os
from dotenv import load_dotenv

load_dotenv()

# Get the JWT secret key from environment variables or use a default for development
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

def verify_password(plain_password, hashed_password):
    return _hash.bcrypt.verify(plain_password, hashed_password)

def get_password_hash(password):
    return _hash.bcrypt.hash(password)

def authenticate_user(db_session, email: str, password: str):
    user = repository.get_user_by_email(db_session, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db_session: Session = Depends(db.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        print("[DEBUG] JWT sub/email:", email)  # Debug print
        if email is None:
            raise credentials_exception
        token_data = user_schema.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = repository.get_user_by_email(db_session, token_data.email)
    print("[DEBUG] User found in DB:", user)  # Debug print
    if user is None:
        raise credentials_exception
    return user

@router.get("/{email}", response_model=user_schema.User)
def get_user(email: str, db_session: Session = Depends(db.get_db)):
    user = repository.get_user_by_email(db_session, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=user_schema.User)
def create_user(user: user_schema.UserCreate, db_session: Session = Depends(db.get_db)):
    db_user = repository.get_user_by_email(db_session, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password before storing
    hashed_password = get_password_hash(user.password)
    return repository.create_user(db_session, user.email, hashed_password)

@router.post("/token", response_model=user_schema.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(db.get_db)):
    user = authenticate_user(db_session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=user_schema.User)
async def read_users_me(current_user=Depends(get_current_user)):
    return current_user
