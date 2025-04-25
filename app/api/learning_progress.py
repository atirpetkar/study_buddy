# app/api/learning_progress.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
import datetime

from app.models import db, repository
from app.schemas.learning_progress import (
    LearningDashboardResponse, 
    TopicProgressResponse,
    LearningActivityRequest,
    RecommendationResponse,
    SpacedRepetitionSchedule
)
from app.core.learning_manager import LearningManager
from app.core.study_planner import StudyPlanGenerator
from app.core.spaced_repetition import SpacedRepetitionScheduler

router = APIRouter()
learning_manager = LearningManager()
study_planner = StudyPlanGenerator()
spaced_repetition = SpacedRepetitionScheduler()

@router.get("/dashboard/{user_id}", response_model=LearningDashboardResponse)
async def get_learning_dashboard(user_id: str, db_session = Depends(db.get_db)):
    """Get a comprehensive learning dashboard for a student"""
    try:
        # Get progress data from learning manager
        dashboard = await learning_manager.generate_dashboard(db_session, user_id)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard: {str(e)}")

@router.get("/topic/{user_id}/{topic}", response_model=TopicProgressResponse)
async def get_topic_progress(user_id: str, topic: str, db_session = Depends(db.get_db)):
    """Get detailed progress for a specific topic"""
    try:
        topic_progress = await learning_manager.get_topic_progress(db_session, user_id, topic)
        return topic_progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving topic progress: {str(e)}")

@router.post("/activity", response_model=Dict[str, Any])
async def record_learning_activity(request: LearningActivityRequest, db_session = Depends(db.get_db)):
    """Record a learning activity and update progress"""
    try:
        result = await learning_manager.record_activity(
            db_session,
            user_id=request.user_id,
            activity_type=request.activity_type,
            topic=request.topic,
            details=request.details
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording activity: {str(e)}")

@router.get("/recommendations/{user_id}", response_model=RecommendationResponse)
async def get_study_recommendations(user_id: str, db_session = Depends(db.get_db)):
    """Get personalized study recommendations based on progress"""
    try:
        recommendations = await learning_manager.generate_recommendations(db_session, user_id)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")
    
@router.get("/schedule/{user_id}", response_model=SpacedRepetitionSchedule)
async def get_spaced_repetition_schedule(user_id: str, days: int = 7, db_session = Depends(db.get_db)):
    """Get spaced repetition schedule for upcoming days"""
    try:
        schedule = await learning_manager.get_spaced_repetition_schedule(db_session, user_id, days)
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating schedule: {str(e)}")

@router.post("/plan/{user_id}", response_model=Dict[str, Any])
async def generate_study_plan(user_id: str, db_session = Depends(db.get_db)):
    """Generate a personalized study plan based on progress data"""
    try:
        # Get progress data from learning manager
        progress_data = await learning_manager.get_all_progress(db_session, user_id)
        
        # Generate study plan
        plan = await study_planner.generate_plan(
            db_session,
            user_id=user_id,
            progress_data=progress_data
        )
        
        # Save plan to database
        saved_plan = repository.create_study_plan(db_session, user_id, plan)
        
        return {
            "plan_id": saved_plan.id,
            "plan": plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating study plan: {str(e)}")

@router.post("/flashcard/review", response_model=Dict[str, Any])
async def record_flashcard_review(
    flashcard_id: str, 
    card_id: str, 
    user_id: str, 
    confidence: int, 
    db_session = Depends(db.get_db)
):
    """Record a flashcard review and schedule the next review"""
    try:
        if confidence < 1 or confidence > 5:
            raise HTTPException(status_code=400, detail="Confidence must be between 1 and 5")
        
        result = await spaced_repetition.update_flashcard_schedule(
            db_session,
            user_id=user_id,
            flashcard_id=flashcard_id,
            card_id=card_id,
            confidence=confidence
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording flashcard review: {str(e)}")

@router.get("/flashcard/due/{user_id}", response_model=List[Dict[str, Any]])
async def get_due_flashcards(user_id: str, db_session = Depends(db.get_db)):
    """Get flashcards that are due for review"""
    try:
        due_flashcards = await spaced_repetition.get_due_flashcards(db_session, user_id)
        return due_flashcards
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving due flashcards: {str(e)}")