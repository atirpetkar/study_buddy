# repository.py: Database CRUD operations for models
import datetime
import json
from sqlalchemy import and_, func
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


# Add to app/models/repository.py
def create_flashcards(db, user_id: str, document_id: str, flashcard_content: Dict[str, Any]):
    """Create a new flashcard set in the database"""
    import uuid
    flashcard = models.Flashcard(
        id=str(uuid.uuid4()),
        user_id=user_id,
        related_document_id=document_id,
        flashcard_content=json.dumps(flashcard_content)
    )
    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)
    return flashcard

def get_flashcards(db, flashcard_id: str):
    """Get flashcards by ID"""
    flashcard = db.query(models.Flashcard).filter(models.Flashcard.id == flashcard_id).first()
    if not flashcard:
        return None
    content = json.loads(flashcard.flashcard_content) if flashcard.flashcard_content else {}
    return {
        "id": flashcard.id,
        "user_id": flashcard.user_id,
        "document_id": flashcard.related_document_id,
        "created_at": flashcard.created_at.isoformat(),
        "content": content
    }

def record_flashcard_review(db, flashcard_id: str, user_id: str, confidence: int):
    """Record a flashcard review with confidence rating and schedule next review"""
    import uuid
    import datetime
    now = datetime.datetime.utcnow()
    days_to_next_review = {
        1: 1,
        2: 3,
        3: 7,
        4: 14,
        5: 30
    }.get(confidence, 3)
    next_review = now + datetime.timedelta(days=days_to_next_review)
    review = models.FlashcardReview(
        id=str(uuid.uuid4()),
        flashcard_id=flashcard_id,
        user_id=user_id,
        confidence=confidence,
        next_review_at=next_review
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

def get_flashcards_due_for_review(db, user_id: str):
    """Get flashcards that are due for review"""
    now = datetime.datetime.utcnow()
    
    # Get the latest review for each flashcard
    latest_reviews = db.query(
        models.FlashcardReview.flashcard_id,
        func.max(models.FlashcardReview.reviewed_at).label('latest_review')
    ).filter(
        models.FlashcardReview.user_id == user_id
    ).group_by(
        models.FlashcardReview.flashcard_id
    ).subquery()
    
    # Join with reviews to get the next_review_at date
    due_reviews = db.query(
        models.FlashcardReview
    ).join(
        latest_reviews,
        and_(
            models.FlashcardReview.flashcard_id == latest_reviews.c.flashcard_id,
            models.FlashcardReview.reviewed_at == latest_reviews.c.latest_review
        )
    ).filter(
        models.FlashcardReview.next_review_at <= now
    ).all()
    
    # Get the flashcards
    flashcard_ids = [review.flashcard_id for review in due_reviews]
    flashcards = db.query(models.Flashcard).filter(models.Flashcard.id.in_(flashcard_ids)).all()
    
    result = []
    for flashcard in flashcards:
        content = json.loads(flashcard.flashcard_content) if flashcard.flashcard_content else {}
        result.append({
            "id": flashcard.id,
            "user_id": flashcard.user_id,
            "document_id": flashcard.related_document_id,
            "created_at": flashcard.created_at.isoformat(),
            "content": content
        })
    
    return result

def create_study_plan(db, user_id: str, plan_data: Dict[str, Any]):
    """Create a new study plan in the database"""
    import uuid
    study_plan = models.StudyPlan(
        id=str(uuid.uuid4()),
        user_id=user_id,
        schedule=json.dumps(plan_data)
    )
    db.add(study_plan)
    db.commit()
    db.refresh(study_plan)
    return study_plan

def get_study_plans(db, user_id: str, limit: int = 5):
    """Get recent study plans for a user"""
    plans = db.query(models.StudyPlan).filter(
        models.StudyPlan.user_id == user_id
    ).order_by(models.StudyPlan.generated_at.desc()).limit(limit).all()
    return [{
        "id": plan.id,
        "user_id": plan.user_id,
        "generated_at": plan.generated_at.isoformat(),
        "schedule": json.loads(plan.schedule) if plan.schedule else {}
    } for plan in plans]

def update_topic_progress(db, user_id: str, topic: str, 
                         activity_type: str, performance: float, 
                         confidence: float = None):
    """Update progress for a topic"""
    import datetime
    import uuid
    progress = db.query(models.ProgressTracking).filter(
        models.ProgressTracking.user_id == user_id,
        models.ProgressTracking.topic == topic
    ).first()
    now = datetime.datetime.utcnow()
    if progress:
        current_proficiency = progress.proficiency
        weights = {
            "quiz": 0.7,
            "flashcard": 0.5,
            "chat": 0.3
        }
        activity_weight = weights.get(activity_type, 0.5)
        updated_proficiency = (performance * activity_weight) + (current_proficiency * (1 - activity_weight))
        if confidence is not None:
            updated_confidence = (confidence * 0.6) + (progress.confidence * 0.4)
        else:
            if updated_proficiency > current_proficiency:
                updated_confidence = min(1.0, progress.confidence + 0.1)
            else:
                updated_confidence = max(0.1, progress.confidence - 0.05)
        progress.proficiency = updated_proficiency
        progress.confidence = updated_confidence
        progress.last_interaction = now
        progress.interaction_type = activity_type
        db.commit()
        db.refresh(progress)
        return progress
    else:
        if confidence is None:
            confidence = 0.5
        new_progress = models.ProgressTracking(
            id=str(uuid.uuid4()),
            user_id=user_id,
            topic=topic,
            proficiency=performance,
            confidence=confidence,
            interaction_type=activity_type
        )
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)
        return new_progress
    
# Add these functions to app/models/repository.py

def get_study_plan(db, plan_id: str):
    """Get a specific study plan by ID"""
    study_plan = db.query(models.StudyPlan).filter(
        models.StudyPlan.id == plan_id
    ).first()
    
    if not study_plan:
        return None
    
    plan_data = json.loads(study_plan.schedule) if study_plan.schedule else {}
    
    return {
        "plan_id": study_plan.id,
        "plan": plan_data
    }

def get_user_profile(db, user_id: str):
    """Get user profile data"""
    profile = db.query(models.UserProfile).filter(
        models.UserProfile.user_id == user_id
    ).first()
    
    if not profile:
        return None
    
    # Parse JSON fields
    study_preferences = {}
    try:
        if profile.study_preferences:
            study_preferences = json.loads(profile.study_preferences)
    except:
        pass
    
    initial_topics = []
    try:
        if profile.initial_topics:
            initial_topics = json.loads(profile.initial_topics)
    except:
        pass
    
    goals = []
    try:
        if profile.goals:
            goals = json.loads(profile.goals)
    except:
        pass
    
    return {
        "user_id": profile.user_id,
        "exam_type": profile.exam_type,
        "study_preferences": study_preferences,
        "available_study_time": profile.available_study_time,
        "topics": initial_topics,
        "goals": goals,
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat()
    }

def create_user_profile(db, user_id: str, profile_data: Dict[str, Any]):
    """Create a new user profile"""
    # Convert complex types to JSON strings
    study_preferences = json.dumps(profile_data.get("study_preferences", {}))
    initial_topics = json.dumps(profile_data.get("initial_topics", []))
    goals = json.dumps(profile_data.get("goals", []))
    
    profile = models.UserProfile(
        user_id=user_id,
        exam_type=profile_data.get("exam_type"),
        study_preferences=study_preferences,
        available_study_time=profile_data.get("available_study_time"),
        initial_topics=initial_topics,
        goals=goals
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_user_profile(db, user_id: str, profile_data: Dict[str, Any]):
    """Update an existing user profile"""
    profile = db.query(models.UserProfile).filter(
        models.UserProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise ValueError(f"Profile not found for user {user_id}")
    
    # Update fields that are present
    if "exam_type" in profile_data:
        profile.exam_type = profile_data["exam_type"]
        
    if "available_study_time" in profile_data:
        profile.available_study_time = profile_data["available_study_time"]
        
    if "study_preferences" in profile_data:
        profile.study_preferences = json.dumps(profile_data["study_preferences"])
        
    if "goals" in profile_data:
        profile.goals = json.dumps(profile_data["goals"])
        
    if "topics" in profile_data:
        profile.initial_topics = json.dumps(profile_data["topics"])
    
    # Update timestamp
    profile.updated_at = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(profile)
    return profile

def save_study_plan_progress(db, plan_id: str, user_id: str, completed_activities: List[Dict[str, Any]]):
    """Record progress on a study plan"""
    # Create a new model for this or just use a generic table
    
    # For now, let's create a simple structure in the existing conversation table
    progress_data = {
        "plan_id": plan_id,
        "completed_activities": completed_activities,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    
    conversation = models.Conversation(
        user_id=user_id,
        message="Study plan progress update",
        response=json.dumps(progress_data),
        source="study_plan_progress"
    )
    
    db.add(conversation)
    db.commit()
    
    return conversation.id

def get_study_plan_progress(db, user_id: str, plan_id: str = None):
    """Get progress records for study plans"""
    
    query = db.query(models.Conversation).filter(
        models.Conversation.user_id == user_id,
        models.Conversation.source == "study_plan_progress"
    )
    
    if plan_id:
        # Filter for specific plan
        query = query.filter(models.Conversation.response.like(f'%"plan_id": "{plan_id}"%'))
    
    progress_records = query.order_by(models.Conversation.created_at.desc()).all()
    
    results = []
    for record in progress_records:
        try:
            progress_data = json.loads(record.response)
            results.append({
                "id": record.id,
                "plan_id": progress_data.get("plan_id"),
                "completed_activities": progress_data.get("completed_activities", []),
                "timestamp": record.created_at.isoformat()
            })
        except:
            # Skip if JSON parsing fails
            continue
    
    return results

# Add to app/models/repository.py
def create_study_session(db, user_id: str, content: str):
    """Create a new study session"""
    import uuid
    session = models.StudySession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        content=content
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_study_session(db, session_id: str):
    """Get a study session by ID"""
    return db.query(models.StudySession).filter(models.StudySession.id == session_id).first()

def update_study_session(db, session_id: str, content: str):
    """Update a study session"""
    session = db.query(models.StudySession).filter(models.StudySession.id == session_id).first()
    if session:
        session.content = content
        session.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(session)
    return session

def get_user_study_sessions(db, user_id: str, limit: int = 10):
    """Get study sessions for a user"""
    return db.query(models.StudySession).filter(
        models.StudySession.user_id == user_id
    ).order_by(models.StudySession.created_at.desc()).limit(limit).all()