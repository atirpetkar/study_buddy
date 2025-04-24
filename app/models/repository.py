# repository.py: Database CRUD operations for models
from sqlalchemy.orm import Session
from . import models
# Add at the top of app/models/repository.py
from typing import List, Dict, Any
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
# Add to app/models/repository.py
def get_user_by_id(db, user_id: str):
    """Get a user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_conversations(db, user_id: str, limit: int = 20):
    """Get the most recent conversations for a user"""
    return db.query(models.Conversation)\
        .filter(models.Conversation.user_id == user_id)\
        .order_by(models.Conversation.created_at.desc())\
        .limit(limit)\
        .all()

def save_conversation(db, user_id: str, message: str, response: str, sources: List[str] = None):
    """Save a conversation to the database"""
    source_str = ", ".join(sources) if sources else ""
    
    conversation = models.Conversation(
        user_id=user_id,
        message=message,
        response=response,
        source=source_str
    )
    
    db.add(conversation)
    db.commit()
    
    return conversation
