# app/core/session_orchestrator.py
from typing import Dict, Any, List, Optional
import json
import datetime
import uuid

class SessionOrchestrator:
    """
    Orchestrates study sessions by planning and executing 
    a sequence of learning activities based on a single document or topic.
    """
    
    def __init__(self):
        """Initialize the session orchestrator"""
        self.active_sessions = {}
    
    async def create_quick_session(self, user_id: str, topic: str, duration_minutes: int = 15, 
                                 db = None, vector_client = None) -> Dict[str, Any]:
        """
        Create a quick study session with a balanced set of activities
        
        Args:
            user_id: User ID
            topic: Topic to study
            duration_minutes: Session duration in minutes (default: 15)
            db: Optional database session
            vector_client: Optional vector store client
            
        Returns:
            Session plan
        """
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Get context for the topic if vector_client available
        context = ""
        if vector_client:
            from app.utils.context_retrieval import retrieve_topic_context
            context_result = await retrieve_topic_context(
                vector_client,
                topic,
                min_chunks=3,
                max_chunks=7
            )
            context = context_result.get("context", "")
        
        # Calculate activity durations based on total time
        intro_time = min(5, duration_minutes // 5)
        remaining_time = duration_minutes - intro_time
        
        # For shorter sessions, pick either flashcards or quiz, not both
        if duration_minutes <= 10:
            activities = [
                {
                    "type": "introduction",
                    "duration_minutes": intro_time,
                    "description": f"Quick introduction to {topic}",
                    "parameters": {"topic": topic}
                },
                {
                    "type": "flashcard",
                    "duration_minutes": remaining_time,
                    "description": f"Review key concepts in {topic}",
                    "parameters": {
                        "num_cards": min(5, remaining_time // 2),
                        "topic": topic
                    }
                }
            ]
        else:
            # For longer sessions, include multiple activity types
            flashcard_time = remaining_time // 3
            quiz_time = remaining_time // 3
            summary_time = remaining_time - flashcard_time - quiz_time
            
            activities = [
                {
                    "type": "introduction",
                    "duration_minutes": intro_time,
                    "description": f"Introduction to {topic}",
                    "parameters": {"topic": topic}
                },
                {
                    "type": "flashcard",
                    "duration_minutes": flashcard_time,
                    "description": f"Review key concepts in {topic}",
                    "parameters": {
                        "num_cards": min(5, flashcard_time // 2),
                        "topic": topic
                    }
                },
                {
                    "type": "quiz",
                    "duration_minutes": quiz_time,
                    "description": f"Test your knowledge of {topic}",
                    "parameters": {
                        "num_questions": min(3, quiz_time // 3),
                        "difficulty": "medium",
                        "topic": topic
                    }
                },
                {
                    "type": "summary",
                    "duration_minutes": summary_time,
                    "description": f"Review what you've learned about {topic}",
                    "parameters": {"topic": topic}
                }
            ]
        
        # Create the session plan
        plan = {
            "session_id": session_id,
            "user_id": user_id,
            "topic": topic,
            "duration_minutes": duration_minutes,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "context": context,
            "activities": activities,
            "status": "planned",
            "current_activity_index": 0
        }
        
        # Store the active session
        self.active_sessions[session_id] = plan
        
        # Save to database if possible
        if db:
            from app.models import repository
            session_record = repository.create_study_session(db, user_id, json.dumps(plan))
            plan["record_id"] = session_record.id
        
        return plan
    
    async def execute_activity(self, session_id: str, activity_index: int = None, 
                              db = None) -> Dict[str, Any]:
        """
        Execute a specific activity in a session
        
        Args:
            session_id: Session ID
            activity_index: Optional activity index, defaults to current
            db: Optional database session
            
        Returns:
            Result of the activity execution
        """
        # Check if session exists
        if session_id not in self.active_sessions:
            if db:
                # Try to load from database
                from app.models import repository
                session_record = repository.get_study_session(db, session_id)
                if session_record:
                    self.active_sessions[session_id] = json.loads(session_record.content)
                else:
                    return {"error": f"Session {session_id} not found"}
            else:
                return {"error": f"Session {session_id} not found"}
        
        # Get session plan
        plan = self.active_sessions[session_id]
        
        # Determine activity index
        if activity_index is None:
            activity_index = plan["current_activity_index"]
        
        # Check if index is valid
        if activity_index < 0 or activity_index >= len(plan["activities"]):
            return {"error": f"Invalid activity index: {activity_index}"}
        
        # Get the activity
        activity = plan["activities"][activity_index]
        
        # Get message processor
        from app.core.agent import get_message_processor
        processor = get_message_processor()
        
        # Execute activity based on type
        result = await self._execute_activity(
            activity["type"],
            activity["parameters"],
            plan["context"],
            plan["user_id"],
            processor
        )
        
        # Update session state
        plan["last_activity_index"] = activity_index
        plan["current_activity_index"] = activity_index + 1
        if plan["current_activity_index"] >= len(plan["activities"]):
            plan["status"] = "completed"
        else:
            plan["status"] = "in_progress"
        
        # Store activity result
        if "results" not in plan:
            plan["results"] = {}
        plan["results"][str(activity_index)] = {
            "activity_type": activity["type"],
            "executed_at": datetime.datetime.utcnow().isoformat(),
            "result": result
        }
        
        # Update in database if possible
        if db:
            from app.models import repository
            repository.update_study_session(db, session_id, json.dumps(plan))
        
        return {
            "session_id": session_id,
            "activity": activity,
            "result": result,
            "next_activity_index": plan["current_activity_index"] if plan["status"] != "completed" else None,
            "status": plan["status"]
        }
    
    async def _execute_activity(self, activity_type: str, parameters: Dict[str, Any], 
                              context: str, user_id: str, processor) -> str:
        """
        Execute a specific activity
        
        Args:
            activity_type: Type of activity
            parameters: Activity parameters
            context: Context information
            user_id: User ID
            processor: Message processor
            
        Returns:
            Result of the activity
        """
        # Execute different activities based on type
        if activity_type == "introduction":
            return await self._execute_introduction(parameters, context, user_id, processor)
        elif activity_type == "quiz":
            return await self._execute_quiz(parameters, context, user_id, processor)
        elif activity_type == "flashcard":
            return await self._execute_flashcard(parameters, context, user_id, processor)
        elif activity_type == "summary":
            return await self._execute_summary(parameters, context, user_id, processor)
        else:
            return f"Unknown activity type: {activity_type}"
    
    async def _execute_introduction(self, parameters: Dict[str, Any], context: str, 
                                  user_id: str, processor) -> str:
        """Execute an introduction activity"""
        topic = parameters.get("topic", "the topic")
        prompt = f"Create a brief, engaging introduction to {topic} that will motivate the student to learn more. Keep it concise, under 150 words."
        
        result = await processor.process_message(
            user_id=user_id,
            message=prompt,
            mode="chat",
            vector_search_client=None
        )
        
        return result["response"]
    
    async def _execute_quiz(self, parameters: Dict[str, Any], context: str, user_id: str, processor) -> str:
        """Execute a quiz activity"""
        topic = parameters.get("topic", "the topic")
        num_questions = parameters.get("num_questions", 3)
        difficulty = parameters.get("difficulty", "medium")
        
        prompt = f"Create a quick quiz about {topic} with {num_questions} questions at {difficulty} difficulty level."
        
        result = await processor.process_message(
            user_id=user_id,
            message=prompt,
            mode="quiz",
            vector_search_client=None
        )
        
        return result["response"]
    
    async def _execute_flashcard(self, parameters: Dict[str, Any], context: str, user_id: str, processor) -> str:
        """Execute a flashcard activity"""
        topic = parameters.get("topic", "the topic")
        num_cards = parameters.get("num_cards", 5)
        
        prompt = f"Create {num_cards} flashcards covering the key concepts of {topic}."
        
        result = await processor.process_message(
            user_id=user_id,
            message=prompt,
            mode="flashcard",
            vector_search_client=None
        )
        
        return result["response"]
    
    async def _execute_summary(self, parameters: Dict[str, Any], context: str, user_id: str, processor) -> str:
        """Execute a summary activity"""
        topic = parameters.get("topic", "the topic")
        prompt = f"Create a brief summary of the key points about {topic}, highlighting what's most important to remember. Keep it concise, under 150 words."
        
        result = await processor.process_message(
            user_id=user_id,
            message=prompt,
            mode="chat",
            vector_search_client=None
        )
        
        return result["response"]
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID"""
        return self.active_sessions.get(session_id)
    
    def get_active_sessions(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get all active sessions, optionally filtered by user ID"""
        if user_id:
            return [s for s in self.active_sessions.values() if s["user_id"] == user_id]
        return list(self.active_sessions.values())