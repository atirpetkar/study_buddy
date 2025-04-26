# app/api/study_plan.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional

from app.models import db, repository
from app.schemas.study_plan import (
    AdvancedStudyPlanRequest,
    StudyPlanResponse
)
from app.core.advanced_study_planner import AdvancedStudyPlanGenerator
from app.core.personalization_engine import PersonalizationEngine
from app.core.vector_store import get_vector_store_client
from app.core.agent import get_message_processor

router = APIRouter()
study_planner = AdvancedStudyPlanGenerator()
personalization_engine = PersonalizationEngine()

@router.post("/advanced", response_model=Dict[str, Any])
async def generate_advanced_study_plan(request: AdvancedStudyPlanRequest, db_session = Depends(db.get_db)):
    """Generate an advanced, personalized study plan based on document analysis"""
    try:
        vector_client = get_vector_store_client()
        processor = get_message_processor()
        
        # Get learning style
        learning_style = await personalization_engine.analyze_learning_style(
            db_session, 
            request.user_id
        )
        
        # Generate the advanced plan
        plan = await study_planner.generate_advanced_plan(
            db_session,
            user_id=request.user_id,
            days=request.days,
            topic_focus=request.topic_focus,
            learning_style=learning_style,
            vector_client=vector_client,
            processor=processor
        )
        
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advanced study plan: {str(e)}")

@router.get("/history/{user_id}", response_model=List[Dict[str, Any]])
async def get_study_plan_history(user_id: str, limit: int = 5, db_session = Depends(db.get_db)):
    """Get historical study plans for a user"""
    try:
        plans = repository.get_study_plans(db_session, user_id, limit)
        return plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving study plan history: {str(e)}")

@router.get("/{plan_id}", response_model=Dict[str, Any])
async def get_study_plan(plan_id: str, db_session = Depends(db.get_db)):
    """Get a specific study plan by ID"""
    try:
        plan = repository.get_study_plan(db_session, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Study plan not found")
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving study plan: {str(e)}")