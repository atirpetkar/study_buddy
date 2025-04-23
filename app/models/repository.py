# repository.py: Database CRUD operations for models
from sqlalchemy.orm import Session
from . import models

# Example CRUD operation: Get user by email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Example CRUD operation: Create a new user
def create_user(db: Session, email: str, hashed_password: str):
    user = models.User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Add more CRUD functions for other models as needed
