# app/api/session.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json

from app.models import db, repository
from app.core.factory import get_factory
from app.core.vector_store import get_vector_store_client

class QuickSessionRequest(BaseModel):
    user_id: str
    topic: str
    duration_minutes: int = 15

class ActivityExecuteRequest(BaseModel):
    session_id: str
    activity_index: Optional[int] = None

router = APIRouter()

@router.post("/quick", response_model=Dict[str, Any])
async def create_quick_session(request: QuickSessionRequest, db_session = Depends(db.get_db)):
    """Create a quick study session"""
    try:
        # Get factory and session orchestrator
        factory = get_factory()
        orchestrator = factory.get_session_orchestrator()
        
        # Get vector client for context retrieval
        vector_client = get_vector_store_client()
        
        # Create the session
        plan = await orchestrator.create_quick_session(
            user_id=request.user_id,
            topic=request.topic,
            duration_minutes=request.duration_minutes,
            db=db_session,
            vector_client=vector_client
        )
        
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating study session: {str(e)}")

@router.post("/execute", response_model=Dict[str, Any])
async def execute_session_activity(request: ActivityExecuteRequest, db_session = Depends(db.get_db)):
    """Execute an activity in a study session"""
    try:
        # Get factory and session orchestrator
        factory = get_factory()
        orchestrator = factory.get_session_orchestrator()
        
        # Execute the activity
        result = await orchestrator.execute_activity(
            session_id=request.session_id,
            activity_index=request.activity_index,
            db=db_session
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing activity: {str(e)}")

@router.get("/{session_id}", response_model=Dict[str, Any])
async def get_session(session_id: str, db_session = Depends(db.get_db)):
    """Get a study session by ID"""
    try:
        # Get factory and session orchestrator
        factory = get_factory()
        orchestrator = factory.get_session_orchestrator()
        
        # Get the session
        session = orchestrator.get_session(session_id)
        
        # If not found in memory, try the database
        if not session:
            record = repository.get_study_session(db_session, session_id)
            if record:
                session = json.loads(record.content)
            else:
                raise HTTPException(status_code=404, detail="Session not found")
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@router.get("/user/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_sessions(user_id: str, db_session = Depends(db.get_db)):
    """Get all sessions for a user"""
    try:
        # Get from database
        records = repository.get_user_study_sessions(db_session, user_id)
        
        sessions = []
        for record in records:
            try:
                session = json.loads(record.content)
                sessions.append(session)
            except:
                continue
        
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user sessions: {str(e)}")