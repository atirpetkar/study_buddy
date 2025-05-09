# app/schemas/user.py: Pydantic schemas for User
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    hashed_password: str

class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True
