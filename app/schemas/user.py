# app/schemas/user.py: Pydantic schemas for User
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    hashed_password: str

class User(UserBase):
    id: str
    created_at: str

    class Config:
        orm_mode = True
