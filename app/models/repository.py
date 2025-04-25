# repository.py: Database CRUD operations for models
import json
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

# Quiz-related CRUD operations

def create_quiz(db, user_id: str, document_id: str, quiz_content: Dict[str, Any]):
    """Create a new quiz in the database"""
    quiz = models.Quiz(
        user_id=user_id,
        related_document_id=document_id,
        quiz_content=json.dumps(quiz_content)
    )
    
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz

def get_quiz(db, quiz_id: str):
    """Get a quiz by ID"""
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if not quiz:
        return None
    
    # Parse the quiz content from JSON
    quiz_content = json.loads(quiz.quiz_content) if quiz.quiz_content else {}
    
    return {
        "id": quiz.id,
        "user_id": quiz.user_id,
        "document_id": quiz.related_document_id,
        "created_at": quiz.created_at.isoformat(),
        "content": quiz_content
    }

def save_quiz_attempt(db, quiz_id: str, user_id: str, answers: Dict[str, str], score: float):
    """Save a quiz attempt to the database"""
    attempt = models.QuizAttempt(
        quiz_id=quiz_id,
        user_id=user_id,
        answers=json.dumps(answers),
        score=score
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt

def get_quiz_attempts(db, user_id: str, quiz_id: str = None):
    """Get quiz attempts for a user, optionally filtered by quiz ID"""
    query = db.query(models.QuizAttempt).filter(models.QuizAttempt.user_id == user_id)
    
    if quiz_id:
        query = query.filter(models.QuizAttempt.quiz_id == quiz_id)
    
    attempts = query.order_by(models.QuizAttempt.taken_at.desc()).all()
    
    return [{
        "id": attempt.id,
        "quiz_id": attempt.quiz_id,
        "taken_at": attempt.taken_at.isoformat(),
        "score": attempt.score,
        "answers": json.loads(attempt.answers) if attempt.answers else {}
    } for attempt in attempts]

def update_progress(db, user_id: str, topic: str, results: Dict[str, Any]):
    """Update student progress based on quiz results"""
    # Get existing progress for this topic
    progress = db.query(models.ProgressTracking).filter(
        models.ProgressTracking.user_id == user_id,
        models.ProgressTracking.topic == topic
    ).first()
    
    # Calculate new proficiency score (simple weighted average)
    new_proficiency = results["score"]["percentage"] / 100  # Convert to 0-1 scale
    
    if progress:
        # Update existing progress
        current_proficiency = progress.proficiency
        # Weight is 0.7 for new result, 0.3 for previous knowledge
        updated_proficiency = (new_proficiency * 0.7) + (current_proficiency * 0.3)
        
        progress.proficiency = updated_proficiency
        progress.confidence = min(1.0, progress.confidence + 0.1) if new_proficiency > 0.7 else max(0.1, progress.confidence - 0.1)
        progress.last_interaction = datetime.datetime.utcnow()
        progress.interaction_type = "quiz"
        
        db.commit()
        db.refresh(progress)
        return progress
    else:
        # Create new progress entry
        new_progress = models.ProgressTracking(
            user_id=user_id,
            topic=topic,
            proficiency=new_proficiency,
            confidence=0.5,  # Start with neutral confidence
            interaction_type="quiz"
        )
        
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)
        return new_progress
    

def get_document_content(db, document_id: str):
    """Get the full content of a document"""
    # Get document chunks from database
    chunks = db.query(models.DocumentChunk).filter(
        models.DocumentChunk.document_id == document_id
    ).order_by(models.DocumentChunk.chunk_index).all()
    
    if not chunks:
        return None
    
    # Combine chunks into full document
    content = "\n".join([chunk.chunk_text for chunk in chunks])
    return content