# app/api/progress.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional

from app.models import db, repository
from app.schemas.progress import ProgressUpdateRequest, ProgressResponse, RecommendationsResponse
from app.core.progress_tracker import ProgressTracker

router = APIRouter()
progress_tracker = ProgressTracker()

@router.post("/update", response_model=Dict[str, Any])
async def update_progress(request: ProgressUpdateRequest, db_session = Depends(db.get_db)):
    """Update student progress for a topic"""
    try:
        updated_progress = progress_tracker.update_topic_progress(
            db_session,
            user_id=request.user_id,
            topic=request.topic,
            activity_type=request.activity_type,
            performance=request.performance,
            confidence=request.confidence
        )
        
        return {
            "success": True,
            "topic": request.topic,
            "proficiency": updated_progress.proficiency,
            "confidence": updated_progress.confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating progress: {str(e)}")

@router.get("/{user_id}", response_model=ProgressResponse)
async def get_progress(user_id: str, topics: Optional[List[str]] = None, db_session = Depends(db.get_db)):
    """Get progress summary for a student"""
    try:
        progress = progress_tracker.get_student_progress(db_session, user_id, topics)
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving progress: {str(e)}")

@router.get("/{user_id}/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(user_id: str, db_session = Depends(db.get_db)):
    """Get personalized study recommendations"""
    try:
        recommendations = progress_tracker.generate_study_recommendations(db_session, user_id)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")