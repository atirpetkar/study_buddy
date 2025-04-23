# app/api/user.py: User API endpoints
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import repository, db
from app.schemas import user as user_schema

router = APIRouter()

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
    return repository.create_user(db_session, user.email, user.hashed_password)
