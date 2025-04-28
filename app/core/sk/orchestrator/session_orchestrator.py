# app/core/sk/orchestrator/session_orchestrator.py
from typing import Dict, Any, List, Optional
import json
import datetime
import uuid
import semantic_kernel as sk
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings

from app.core.session_orchestrator import SessionOrchestrator

class SKSessionOrchestrator(SessionOrchestrator):
    """SK implementation of the session orchestrator"""
    
    def __init__(self):
        """Initialize the SK session orchestrator"""
        super().__init__()
        # Defer the kernel import until needed
        self.kernel = None
    
    def _ensure_kernel(self):
        """Ensure the kernel is initialized"""
        if self.kernel is None:
            # Import here to avoid circular dependency
            from app.core.sk.kernel_factory import get_kernel
            self.kernel = get_kernel()
    
    async def create_quick_session(self, user_id: str, topic: str, duration_minutes: int = 15, 
                                 db = None, vector_client = None) -> Dict[str, Any]:
        """Create a quick study session using SK planning capabilities"""
        # Ensure kernel is initialized
        self._ensure_kernel()
        
        try:
            # Get chat service for planning
            chat_service = self.kernel.get_service("github")
            
            # Create planning prompt for session
            planning_prompt = f"""
            You are a study session planner optimizing for effective learning in {duration_minutes} minutes.
            
            Create a study session plan on "{topic}" that includes a sequence of 2-4 learning activities.
            
            The study session should:
            1. Start with a brief introduction to the topic (3-5 minutes)
            2. Include a balanced mix of activities appropriate for the time available
            3. End with a brief summary if time permits
            
            Return a JSON object with this structure:
            {{
                "activities": [
                    {{
                        "type": "introduction|flashcard|quiz|summary",
                        "duration_minutes": minutes_as_integer,
                        "description": "Brief activity description",
                        "parameters": {{
                            "topic": "{topic}",
                            // Additional parameters for this activity type
                        }}
                    }},
                    // Additional activities...
                ]
            }}
            
            The total duration of all activities must be {duration_minutes} minutes.
            Use shorter/fewer activities for shorter sessions, more activities for longer sessions.
            """
            
            # Create chat history and execution settings
            chat_history = ChatHistory()
            chat_history.add_system_message("You are a study session planner specializing in effective learning sequences.")
            chat_history.add_user_message(planning_prompt)
            
            execution_settings = PromptExecutionSettings()
            
            # Generate the session plan
            completion = await chat_service.get_chat_message_content(chat_history, settings=execution_settings)
            result = completion.content
            
            # Parse result to extract JSON
            import re
            json_match = re.search(r'({.*})', result.replace('\n', ' '), re.DOTALL)
            
            activities = []
            if json_match:
                try:
                    plan_data = json.loads(json_match.group(1))
                    activities = plan_data.get("activities", [])
                except:
                    # Fall back to base implementation if parsing fails
                    return await super().create_quick_session(user_id, topic, duration_minutes, db, vector_client)
            
            # If no activities were parsed, fall back to base implementation
            if not activities:
                return await super().create_quick_session(user_id, topic, duration_minutes, db, vector_client)
                
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
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Create the full session plan
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
            
        except Exception as e:
            print(f"Error creating session with SK: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to the base implementation
            return await super().create_quick_session(user_id, topic, duration_minutes, db, vector_client)
    
    async def execute_activity(self, session_id: str, activity_index: int = None, 
                              db = None) -> Dict[str, Any]:
        """Execute a session activity using SK"""
        # Ensure kernel is initialized
        self._ensure_kernel()
        
        try:
            # Call parent implementation for now - this would be enhanced with SK-specific execution
            return await super().execute_activity(session_id, activity_index, db)
            
        except Exception as e:
            print(f"Error executing activity with SK: {e}")
            # Fall back to the parent implementation
            return await super().execute_activity(session_id, activity_index, db)