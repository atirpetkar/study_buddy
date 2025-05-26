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
    """Create a quick study session - returns immediately with session ID"""
    try:
        # Get factory and session orchestrator
        factory = get_factory()
        orchestrator = factory.get_session_orchestrator()
        
        # Get vector client for context retrieval
        vector_client = get_vector_store_client()
        
        # Map "user123" to "qwe@gmail.com" for consistency with frontend
        user_id = request.user_id
        if user_id == "user123":
            user_id = "qwe@gmail.com"
        
        # Create a minimal session first to avoid UI hanging
        import uuid
        import datetime
        import json
        
        session_id = str(uuid.uuid4())
        
        # Create a minimal initial plan
        initial_plan = {
            "session_id": session_id,
            "user_id": user_id,
            "topic": request.topic,
            "duration_minutes": request.duration_minutes,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "activities": [],
            "status": "initializing",
            "current_activity_index": 0
        }
        
        # Add creation timing metadata
        initial_plan["creation_started_at"] = datetime.datetime.utcnow().isoformat()
        initial_plan["estimated_completion_time"] = "10-30 seconds"
        
        # Save initial session to database immediately
        from app.models import repository
        repository.create_study_session(db_session, user_id, json.dumps(initial_plan))
        
        # Define background task with proper error handling
        async def create_session_background():
            try:
                print(f"🔄 Starting background creation of session {session_id} for topic '{request.topic}'")
                result = await orchestrator.create_quick_session(
                    user_id=user_id,
                    topic=request.topic,
                    duration_minutes=request.duration_minutes,
                    db=db_session,
                    vector_client=vector_client,
                    session_id=session_id
                )
                print(f"✅ Session {session_id} created successfully in background task")
                # Update the result to indicate completion
                result["status"] = "planned"
                result["creation_completed_at"] = datetime.datetime.utcnow().isoformat()
                repository.update_study_session(db_session, session_id, json.dumps(result))
            except Exception as e:
                import traceback
                print(f"❌ Error in background session creation for {session_id}: {str(e)}")
                traceback.print_exc()
                
                # Update session with error status
                error_plan = initial_plan.copy()
                error_plan["status"] = "error"
                error_plan["error_message"] = str(e)
                error_plan["creation_failed_at"] = datetime.datetime.utcnow().isoformat()
                repository.update_study_session(db_session, session_id, json.dumps(error_plan))
        
        # Start session creation in the background (don't await it)
        import asyncio
        asyncio.create_task(create_session_background())
        
        # Return the initial plan with more status details immediately
        initial_plan["status_details"] = "Session creation has been started in the background. Use the session_id to check status."
        return initial_plan
    except Exception as e:
        import traceback
        print(f"❌ Error initiating study session: {str(e)}")
        traceback.print_exc()
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
        
        # Ensure consistent user_id format in the response
        if "user_id" in result and result["user_id"] == "qwe@gmail.com":
            # This ensures the frontend gets the user ID it expects
            result["user_id"] = "user123"
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing activity: {str(e)}")

@router.get("/{session_id}", response_model=Dict[str, Any])
async def get_session(session_id: str, db_session = Depends(db.get_db)):
    """Get a study session by ID with status information"""
    try:
        # Get factory and session orchestrator
        factory = get_factory()
        orchestrator = factory.get_session_orchestrator()
        
        print(f"🔍 Request to get session {session_id}")
        
        # Get the session
        session = orchestrator.get_session(session_id)
        
        # If not found in memory, try the database
        if not session:
            print(f"📊 Session {session_id} not found in memory, checking database")
            record = repository.get_study_session(db_session, session_id)
            if record:
                session = json.loads(record.content)
                # Add status information for UI
                if session.get("status") == "initializing":
                    import datetime
                    created_time_str = session.get("creation_started_at", session.get("created_at"))
                    if created_time_str:
                        try:
                            created_time = datetime.datetime.fromisoformat(created_time_str)
                            current_time = datetime.datetime.utcnow()
                            elapsed_seconds = (current_time - created_time).total_seconds()
                            session["elapsed_time_seconds"] = elapsed_seconds
                            session["status_message"] = f"Creating session for {session.get('topic')} ({elapsed_seconds:.1f} seconds elapsed)"
                        except Exception as e:
                            print(f"⚠️ Error calculating elapsed time: {str(e)}")
                            session["status_message"] = f"Creating session for {session.get('topic')}"
                elif session.get("status") == "planned":
                    session["status_message"] = "Session ready to start"
                elif session.get("status") == "error":
                    session["status_message"] = f"Error: {session.get('error_message', 'Unknown error')}"
            else:
                print(f"❌ Session {session_id} not found in database")
                raise HTTPException(status_code=404, detail="Session not found")
        
        # Ensure consistent user_id format in the response
        if "user_id" in session and session["user_id"] == "qwe@gmail.com":
            # This ensures the frontend gets the user ID it expects
            session["user_id"] = "user123"
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving session: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@router.get("/user/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_sessions(user_id: str, db_session = Depends(db.get_db)):
    """Get all sessions for a user"""
    try:
        # Map "user123" to "qwe@gmail.com" for compatibility with frontend
        # This is a temporary solution until proper authentication is implemented
        if user_id == "user123":
            user_id = "qwe@gmail.com"
            
        # Get from database - our updated repository function now returns parsed sessions
        sessions = repository.get_user_study_sessions(db_session, user_id)
        
        # Ensure user_id consistency in each session
        for session in sessions:
            if "user_id" in session and session["user_id"] == "qwe@gmail.com":
                # This ensures the frontend gets the user ID it expects
                session["user_id"] = "user123"
        
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user sessions: {str(e)}")