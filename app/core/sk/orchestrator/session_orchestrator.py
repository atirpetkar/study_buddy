# app/core/sk/orchestrator/session_orchestrator.py
from typing import Dict, Any, List, Optional
import json
import datetime
import uuid
import semantic_kernel as sk
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
import logging

from app.core.session_orchestrator import SessionOrchestrator

# Get logger for this module
logger = logging.getLogger(__name__)

class SKSessionOrchestrator(SessionOrchestrator):
    """SK implementation of the session orchestrator"""
    
    def __init__(self):
        """Initialize the SK session orchestrator"""
        super().__init__()
        # Defer the kernel import until needed
        self.kernel = None
        logger.debug("SKSessionOrchestrator initialized")
    
    def _ensure_kernel(self):
        """Ensure the kernel is initialized"""
        if self.kernel is None:
            logger.debug("Initializing kernel for the first time")
            # Import here to avoid circular dependency
            from app.core.sk.kernel_factory import get_kernel
            self.kernel = get_kernel()
            logger.debug("Kernel initialized successfully")
        else:
            logger.debug("Kernel already initialized")
    
    async def create_quick_session(self, user_id: str, topic: str, duration_minutes: int = 15, 
                                 db = None, vector_client = None, session_id: str = None) -> Dict[str, Any]:
        """Create a quick study session using SK planning capabilities"""
        logger.debug(f"Starting create_quick_session for user_id={user_id}, topic='{topic}', duration={duration_minutes}, session_id={session_id}")
        
        # Ensure kernel is initialized
        self._ensure_kernel()
        
        try:
            # Get chat service for planning
            logger.debug("Getting chat service for session planning")
            chat_service = self.kernel.get_service("github")
            
            # Create planning prompt for session
            logger.debug("Creating planning prompt")
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
            logger.debug("Setting up chat history and execution settings")
            chat_history = ChatHistory()
            chat_history.add_system_message("You are a study session planner specializing in effective learning sequences.")
            chat_history.add_user_message(planning_prompt)
            
            execution_settings = PromptExecutionSettings()
            
            # Generate the session plan
            logger.debug("Calling chat service to generate session plan")
            completion = await chat_service.get_chat_message_content(chat_history, settings=execution_settings)
            result = completion.content
            logger.debug(f"Received planning response of length {len(result)}")
            
            # Parse result to extract JSON
            logger.debug("Parsing JSON from planning response")
            import re
            json_match = re.search(r'({.*})', result.replace('\n', ' '), re.DOTALL)
            
            activities = []
            if json_match:
                try:
                    logger.debug("JSON pattern found, attempting to parse")
                    plan_data = json.loads(json_match.group(1))
                    activities = plan_data.get("activities", [])
                    logger.debug(f"Successfully parsed {len(activities)} activities")
                except Exception as e:
                    logger.error(f"JSON parsing error: {str(e)}")
                    logger.debug("Falling back to base implementation due to parsing error")
                    return await super().create_quick_session(user_id, topic, duration_minutes, db, vector_client, session_id)
            
            # If no activities were parsed, fall back to base implementation
            if not activities:
                logger.warning("No activities were parsed from the planning response")
                logger.debug("Falling back to base implementation due to no activities")
                return await super().create_quick_session(user_id, topic, duration_minutes, db, vector_client, session_id)
                
            # Get context for the topic if vector_client available
            context = ""
            if vector_client:
                logger.debug("Retrieving topic context from vector store")
                from app.utils.context_retrieval import retrieve_topic_context
                context_result = await retrieve_topic_context(
                    vector_client,
                    topic,
                    min_chunks=3,
                    max_chunks=7
                )
                context = context_result.get("context", "")
                logger.debug(f"Retrieved context of length {len(context)}")
            else:
                logger.debug("No vector client provided, skipping context retrieval")
            
            # Use provided session_id or generate a new one
            if not session_id:
                session_id = str(uuid.uuid4())
                logger.debug(f"Generated new session_id: {session_id}")
            else:
                logger.debug(f"Using provided session_id: {session_id}")
            
            # Create the full session plan
            logger.debug("Creating the final session plan")
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
            logger.debug(f"Storing session {session_id} in active_sessions")
            self.active_sessions[session_id] = plan
            
            # Save to database if possible
            if db:
                logger.debug(f"Saving session {session_id} to database")
                from app.models import repository
                session_record = repository.create_study_session(db, user_id, json.dumps(plan))
                plan["record_id"] = session_record.id
                logger.debug(f"Session saved to database with record_id: {session_record.id}")
            else:
                logger.debug("No database session provided, skipping database save")
            
            logger.debug(f"Session {session_id} creation completed successfully")
            return plan
            
        except Exception as e:
            logger.error(f"Error creating session with SK: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Fall back to the base implementation
            logger.debug("Falling back to base implementation due to exception")
            return await super().create_quick_session(user_id, topic, duration_minutes, db, vector_client, session_id)
    
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