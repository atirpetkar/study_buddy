# app/core/study_planner.py
from typing import Dict, Any, List
import datetime
import json

class StudyPlanGenerator:
    """Generates personalized study plans based on learning progress"""
    
    async def generate_plan(self, db, user_id: str, progress_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a personalized study plan
        
        Args:
            db: Database session
            user_id: User ID
            progress_data: Optional pre-loaded progress data
            
        Returns:
            Dictionary with study plan
        """
        from app.models import models
        
        # If progress data not provided, fetch it
        if not progress_data:
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
            
            progress_data = {
                "user_id": user_id,
                "topics": topics_data
            }
        
        # No topics yet
        if not progress_data.get("topics"):
            return self._generate_empty_plan(user_id)
        
        # Current date
        now = datetime.datetime.utcnow()
        
        # Generate study schedule for the next 7 days
        schedule = []
        
        # Organize topics by priority
        topics_by_priority = self._prioritize_topics(progress_data["topics"])
        
        # Create a 7-day schedule
        for day in range(7):
            current_date = now + datetime.timedelta(days=day)
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Assign topics based on day of week and priority
            day_topics = []
            
            # Each day, focus on 1-3 topics
            topic_count = min(3, len(topics_by_priority))
            
            for i in range(min(topic_count, len(topics_by_priority))):
                # Rotate topics across days
                topic_idx = (i + day) % len(topics_by_priority)
                topic = topics_by_priority[topic_idx]
                
                # Get topic data
                topic_data = progress_data["topics"][topic]
                proficiency = topic_data["proficiency"]
                
                # Recommend activities based on proficiency
                activities = []
                
                if proficiency < 0.4:
                    # Low proficiency - need foundational work
                    activities.append({
                        "type": "tutoring",
                        "duration": 20,
                        "description": f"Tutoring session on {topic} fundamentals"
                    })
                    activities.append({
                        "type": "flashcard",
                        "duration": 10,
                        "description": f"Review basic {topic} flashcards"
                    })
                elif proficiency < 0.7:
                    # Medium proficiency - need practice
                    activities.append({
                        "type": "quiz",
                        "duration": 15,
                        "description": f"Practice quiz on {topic}"
                    })
                    activities.append({
                        "type": "flashcard",
                        "duration": 10,
                        "description": f"Review {topic} flashcards"
                    })
                else:
                    # High proficiency - maintenance
                    activities.append({
                        "type": "flashcard",
                        "duration": 10,
                        "description": f"Quick review of {topic} flashcards"
                    })
                
                day_topics.append({
                    "topic": topic,
                    "activities": activities,
                    "total_duration": sum(a["duration"] for a in activities)
                })
            
            # Add to schedule
            schedule.append({
                "date": date_str,
                "day_of_week": current_date.strftime("%A"),
                "topics": day_topics,
                "total_duration": sum(topic["total_duration"] for topic in day_topics)
            })
        
        # Generate overall weekly goals
        goals = self._generate_weekly_goals(progress_data["topics"])
        
        return {
            "user_id": user_id,
            "generated_at": now.isoformat(),
            "schedule": schedule,
            "weekly_goals": goals
        }
    
    def _generate_empty_plan(self, user_id: str) -> Dict[str, Any]:
        """Generate an empty plan for new users"""
        now = datetime.datetime.utcnow()
        
        # Empty schedule for 7 days
        schedule = []
        for day in range(7):
            current_date = now + datetime.timedelta(days=day)
            date_str = current_date.strftime("%Y-%m-%d")
            
            schedule.append({
                "date": date_str,
                "day_of_week": current_date.strftime("%A"),
                "topics": [],
                "total_duration": 0,
                "suggestion": "Upload study materials and take initial quizzes"
            })
        
        return {
            "user_id": user_id,
            "generated_at": now.isoformat(),
            "schedule": schedule,
            "weekly_goals": [
                "Upload study materials to get started",
                "Take diagnostic quizzes to establish baseline knowledge",
                "Set up your learning profile"
            ]
        }
    
    def _prioritize_topics(self, topics_data: Dict[str, Any]) -> List[str]:
        """
        Sort topics by priority for study planning
        
        Args:
            topics_data: Dictionary of topic data
            
        Returns:
            List of topic names sorted by priority
        """
        # Calculate priority scores
        topic_priorities = []
        
        for topic, data in topics_data.items():
            # Base score - lower proficiency means higher priority
            priority_score = 1.0 - data["proficiency"]
            
            # Adjust for overconfidence (high confidence but low proficiency)
            if data["confidence"] > 0.7 and data["proficiency"] < 0.5:
                priority_score += 0.3
            
            # Adjust for time since last interaction
            if "last_interaction" in data:
                last_interaction = datetime.datetime.fromisoformat(data["last_interaction"])
                days_since = (datetime.datetime.utcnow() - last_interaction).days
                
                # More days = higher priority, capped at 30 days
                priority_score += min(days_since, 30) / 100
            
            topic_priorities.append((topic, priority_score))
        
        # Sort by priority score (higher score = higher priority)
        topic_priorities.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the topic names
        return [topic for topic, _ in topic_priorities]
    
    def _generate_weekly_goals(self, topics_data: Dict[str, Any]) -> List[str]:
        """Generate weekly learning goals based on topic progress"""
        goals = []
        
        # Find weak topics (low proficiency)
        weak_topics = [topic for topic, data in topics_data.items() if data["proficiency"] < 0.5]
        if weak_topics:
            goals.append(f"Improve understanding of {', '.join(weak_topics[:3])}")
        
        # Find topics with good proficiency
        strong_topics = [topic for topic, data in topics_data.items() if data["proficiency"] >= 0.7]
        if strong_topics:
            goals.append(f"Maintain knowledge of {', '.join(strong_topics[:3])}")
        
        # Find overconfident topics
        overconfident = [topic for topic, data in topics_data.items() 
                         if data["confidence"] > 0.7 and data["proficiency"] < 0.5]
        if overconfident:
            goals.append(f"Test and verify understanding of {', '.join(overconfident[:3])}")
        
        # Add a general goal
        goals.append("Complete all scheduled study sessions")
        
        return goals