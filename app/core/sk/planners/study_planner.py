# app/core/sk/planners/study_planner.py
from typing import Dict, Any, List
import json
import semantic_kernel as sk
from semantic_kernel.planning.sequential_planner import SequentialPlanner
from app.core.study_planner import StudyPlanGenerator

class SKStudyPlanGenerator(StudyPlanGenerator):
    """Semantic Kernel implementation of study planning"""
    
    def __init__(self):
        """Initialize the SK study planner"""
        super().__init__()
        # Get the kernel
        from app.core.sk.kernel_factory import get_kernel
        self.kernel = get_kernel()
        # Create planner
        self.planner = SequentialPlanner(self.kernel)
    
    async def generate_plan(self, db, user_id: str, progress_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a personalized study plan using Semantic Kernel planning"""
        # First try to use SK planner
        try:
            # Get progress data if not provided
            if not progress_data:
                # This uses the same code from the parent class
                progress_data = await self._get_progress_data(db, user_id)
            
            # Convert progress data to string format for the planner
            progress_str = json.dumps(progress_data)
            
            # Define the plan
            plan_prompt = f"""
            Generate a personalized study plan for user {user_id} based on their learning progress.
            The plan should cover the next 7 days and include specific activities for each topic.
            
            User progress data:
            {progress_str}
            
            Your plan should include:
            1. Daily schedule with topics and activities
            2. Weekly goals
            3. Recommended focus areas
            
            The plan should be adaptive to the user's proficiency levels and confidence.
            """
            
            # Create the plan with SK planner
            plan = await self.planner.create_plan_async(plan_prompt)
            
            # Execute the plan
            result = await self.kernel.run_async(plan)
            
            # Parse the result
            try:
                plan_data = json.loads(str(result))
                return plan_data
            except:
                # If parsing fails, use the result as a base for the plan
                now = self._get_current_time()
                plan_data = {
                    "user_id": user_id,
                    "generated_at": now.isoformat(),
                    "schedule": self._parse_plan_from_text(str(result), progress_data),
                    "weekly_goals": self._extract_goals_from_text(str(result)),
                }
                return plan_data
                
        except Exception as e:
            print(f"Error generating study plan with SK: {e}")
            # Fall back to the original implementation
            return await super().generate_plan(db, user_id, progress_data)
    
    def _parse_plan_from_text(self, plan_text: str, progress_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse a study plan from free text"""
        # Simplified parsing logic - in a real implementation, this would be more robust
        schedule = []
        import datetime
        now = datetime.datetime.utcnow()
        
        # Extract day sections (simplified)
        import re
        day_sections = re.split(r'Day \d+|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday', plan_text)
        
        # Process each day section
        for i, section in enumerate(day_sections[1:8]):  # Take up to 7 days
            current_date = now + datetime.timedelta(days=i)
            day_of_week = current_date.strftime("%A")
            
            # Try to extract topics and activities
            topics = []
            for topic_name in progress_data.get("topics", {}).keys():
                if topic_name.lower() in section.lower():
                    activities_text = section.lower().split(topic_name.lower())[1].split("topic")[0]
                    activities = []
                    
                    # Try to extract activities
                    if "quiz" in activities_text:
                        activities.append({
                            "type": "quiz",
                            "duration": 15,
                            "description": f"Complete quiz on {topic_name}"
                        })
                    
                    if "flashcard" in activities_text:
                        activities.append({
                            "type": "flashcard",
                            "duration": 10,
                            "description": f"Review flashcards for {topic_name}"
                        })
                    
                    if "read" in activities_text or "study" in activities_text:
                        activities.append({
                            "type": "reading",
                            "duration": 20,
                            "description": f"Read about {topic_name}"
                        })
                    
                    # Add topic if activities were found
                    if activities:
                        topics.append({
                            "topic": topic_name,
                            "activities": activities,
                            "total_duration": sum(a["duration"] for a in activities)
                        })
            
            # Add default topic if none found
            if not topics and i < len(progress_data.get("topics", {}).keys()):
                topic_name = list(progress_data.get("topics", {}).keys())[i % len(progress_data.get("topics", {}).keys())]
                topics.append({
                    "topic": topic_name,
                    "activities": [{
                        "type": "review",
                        "duration": 30,
                        "description": f"Review {topic_name}"
                    }],
                    "total_duration": 30
                })
            
            # Add day to schedule
            schedule.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "day_of_week": day_of_week,
                "topics": topics,
                "total_duration": sum(topic["total_duration"] for topic in topics)
            })
        
        return schedule
    
    def _extract_goals_from_text(self, plan_text: str) -> List[str]:
        """Extract weekly goals from plan text"""
        goals = []
        
        # Look for goals section
        import re
        goals_section = re.search(r'(?:Weekly Goals|Goals|Objectives):(.*?)(?:\n\n|\n[A-Z]|$)', plan_text, re.DOTALL | re.IGNORECASE)
        
        if goals_section:
            goals_text = goals_section.group(1).strip()
            # Extract bullet points or numbered items
            goal_items = re.findall(r'(?:^|\n)(?:\d+\.|[\-\*•])\s*(.*?)(?:\n|$)', goals_text)
            
            if goal_items:
                goals = [item.strip() for item in goal_items if item.strip()]
        
        # Add default goals if none found
        if not goals:
            goals = [
                "Complete all scheduled study sessions",
                "Review progress at the end of the week",
                "Focus on topics with low proficiency"
            ]
        
        return goals