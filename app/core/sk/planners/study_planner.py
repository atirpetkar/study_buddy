# app/core/sk/planners/study_planner.py
from typing import Dict, Any, List, Optional
import json
import datetime
import semantic_kernel as sk
import re  # Added import for regex
from semantic_kernel.planners.sequential_planner import SequentialPlanner
# Import the correct ChatHistory class for Semantic Kernel 1.28.1
from semantic_kernel.contents.chat_history import ChatHistory
from app.core.study_planner import StudyPlanGenerator

# Import the PromptExecutionSettings class to create settings for the chat completion
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings

class SKStudyPlanGenerator(StudyPlanGenerator):
    """Semantic Kernel implementation of study planning"""
    
    def __init__(self):
        """Initialize the SK study planner"""
        super().__init__()
        # Defer the kernel import until it's actually needed
        self.kernel = None
        self.planner = None
    
    def _ensure_kernel(self):
        """Lazy-load the kernel and planner only when needed"""
        if self.kernel is None:
            # Import here to avoid circular dependency
            from app.core.sk.kernel_factory import get_kernel
            self.kernel = get_kernel()
            # Create planner
            self.planner = SequentialPlanner(self.kernel, service_id="study_planner")
    
    async def generate_plan(self, db, user_id: str, progress_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a personalized study plan using Semantic Kernel planning"""
        # Ensure kernel is loaded
        self._ensure_kernel()
        
        try:
            # Get progress data if not provided
            if not progress_data:
                # Use the parent class method to get progress data
                progress_data = await self._get_progress_data(db, user_id)
            
            # Convert progress data to string format for the planner
            progress_json = json.dumps(progress_data, indent=2)
            
            # Create the planner prompt
            plan_prompt = f"""
            You are a specialized study plan generator. Create a 7-day personalized study plan
            for user {user_id} based on their learning progress data below.
            
            PROGRESS DATA:
            {progress_json}
            
            FORMAT:
            Return a JSON object with this structure:
            {{
                "user_id": "{user_id}",
                "generated_at": "current_date_time",
                "schedule": [
                    {{
                        "date": "YYYY-MM-DD",
                        "day_of_week": "Monday",
                        "topics": [
                            {{
                                "topic": "Topic Name",
                                "activities": [
                                    {{
                                        "type": "quiz|flashcard|reading|practice",
                                        "duration": minutes_as_integer,
                                        "description": "Activity description"
                                    }}
                                ],
                                "total_duration": sum_of_activity_durations
                            }}
                        ],
                        "total_duration": sum_of_topic_durations
                    }}
                ],
                "weekly_goals": [
                    "Goal 1",
                    "Goal 2"
                ]
            }}
            
            RULES:
            1. Prioritize topics with low proficiency (< 0.5)
            2. Include topics not studied recently (> 7 days)
            3. Balance activities based on learning needs
            4. Keep daily study time reasonable (30-120 minutes)
            5. Include 2-3 specific weekly goals
            6. Weekly goals should be concrete and measurable
            
            The plan should be adaptive to the student's strengths and weaknesses.
            """
            
            # Execute using SK reasoning
            chat_completion_service = self.kernel.get_service("github")
            
            # Create chat history using the correct import
            chat_history = ChatHistory()
            chat_history.add_system_message("You are a specialized study plan generator that creates personalized learning schedules.")
            chat_history.add_user_message(plan_prompt)
            
            # Create the execution settings required by the get_chat_message_content method
            execution_settings = PromptExecutionSettings()
            
            # Updated to use the correct method in SK 1.28.1 with required settings parameter
            completion = await chat_completion_service.get_chat_message_content(chat_history, settings=execution_settings)
            result = completion.content
            
            # Try to parse the result as JSON
            try:
                plan_data = json.loads(result)
                return plan_data
            except json.JSONDecodeError:
                # If parsing fails, create a structured plan from the text
                
                # Create a basic structure
                now = datetime.datetime.utcnow()
                schedule = []
                
                # Generate a week of dates
                for i in range(7):
                    day_date = now + datetime.timedelta(days=i)
                    schedule.append({
                        "date": day_date.strftime("%Y-%m-%d"),
                        "day_of_week": day_date.strftime("%A"),
                        "topics": self._extract_topics_from_text(result, day_date.strftime("%A")),
                        "total_duration": 60  # Default
                    })
                
                return {
                    "user_id": user_id,
                    "generated_at": now.isoformat(),
                    "schedule": schedule,
                    "weekly_goals": self._extract_goals_from_text(result)
                }
                
        except Exception as e:
            print(f"Error generating study plan with SK: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to the original implementation
            return await super().generate_plan(db, user_id, progress_data)
    
    def _extract_topics_from_text(self, text: str, day_name: str) -> List[Dict[str, Any]]:
        """Extract topics and activities for a day from text"""
        topics = []
        
        # Try to find the section for this day
        day_pattern = rf"{day_name}:?.*?(?=(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)|$)"
        day_match = re.search(day_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if day_match:
            day_text = day_match.group(0)
            
            # Look for topic names
            topic_pattern = r"[*-]\s+([A-Za-z\s]+)(?:\(|:|\n)"
            topic_matches = re.finditer(topic_pattern, day_text)
            
            for topic_match in topic_matches:
                topic_name = topic_match.group(1).strip()
                
                # Extract activities for this topic
                activities = []
                activities_text = day_text[topic_match.end():]
                activity_pattern = r"([A-Za-z\s]+)(?:\((\d+)\s*min(?:utes)?\))?"
                activity_matches = re.finditer(activity_pattern, activities_text)
                
                for i, activity_match in enumerate(activity_matches):
                    if i >= 3:  # Limit to 3 activities per topic
                        break
                        
                    activity_type = "quiz" if "quiz" in activity_match.group(1).lower() else \
                                  "flashcard" if "flashcard" in activity_match.group(1).lower() else \
                                  "reading" if "read" in activity_match.group(1).lower() else "practice"
                                  
                    duration = int(activity_match.group(2)) if activity_match.group(2) else 20
                    
                    activities.append({
                        "type": activity_type,
                        "duration": duration,
                        "description": activity_match.group(1).strip()
                    })
                
                # Add default activity if none found
                if not activities:
                    activities.append({
                        "type": "review",
                        "duration": 30,
                        "description": f"Review {topic_name}"
                    })
                
                # Add topic
                topics.append({
                    "topic": topic_name,
                    "activities": activities,
                    "total_duration": sum(a["duration"] for a in activities)
                })
        
        # If no topics found, add a default topic
        if not topics:
            topics.append({
                "topic": "General Study",
                "activities": [{
                    "type": "review",
                    "duration": 30,
                    "description": "General review session"
                }],
                "total_duration": 30
            })
        
        return topics
    
    def _extract_goals_from_text(self, text: str) -> List[str]:
        """Extract weekly goals from plan text"""
        goals = []
        
        # Look for goals section
        goals_pattern = r"(?:Weekly Goals|Goals|Objectives):?\s*(.*?)(?=$|(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday))"
        goals_match = re.search(goals_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if goals_match:
            goals_text = goals_match.group(1).strip()
            # Extract bullet points or numbered items
            goal_items = re.findall(r'(?:^|\n)(?:\d+\.?|[-*•])\s*(.*?)(?=\n\d+\.?|$|\n[-*•])', goals_text)
            
            if goal_items:
                goals = [item.strip() for item in goal_items if item.strip()]
        
        # Add default goals if none found
        if not goals:
            goals = [
                "Complete all scheduled study sessions",
                "Review progress at the end of the week",
                "Focus on improving weakest topics"
            ]
        
        return goals

    async def _get_progress_data(self, db, user_id: str) -> Dict[str, Any]:
        """Get progress data for a user"""
        # This is a simplified version - you might want to use your existing code
        if not db:
            return {"user_id": user_id, "topics": {}}
            
        from app.models import models
        
        # Get all progress records for this user
        progress_records = db.query(models.ProgressTracking).filter(
            models.ProgressTracking.user_id == user_id
        ).all()
        
        topics_data = {}
        for record in progress_records:
            topics_data[record.topic] = {
                "proficiency": record.proficiency,
                "confidence": record.confidence,
                "last_interaction": record.last_interaction.isoformat()
            }
        
        return {
            "user_id": user_id,
            "topics": topics_data
        }