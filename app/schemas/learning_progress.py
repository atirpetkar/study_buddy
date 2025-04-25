# app/schemas/learning_progress.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class TopicProgressData(BaseModel):
    topic: str
    proficiency: float
    confidence: float
    last_activity_date: str
    activity_history: Optional[List[Dict[str, Any]]] = []
    strengths: List[str]
    weaknesses: List[str]
    
class ActivitySummary(BaseModel):
    total_quizzes: int
    avg_quiz_score: float
    total_flashcards_reviewed: int
    avg_flashcard_confidence: float
    tutoring_sessions: int
    
class LearningDashboardResponse(BaseModel):
    user_id: str
    overall_proficiency: float
    overall_confidence: float
    topics: List[TopicProgressData]
    recent_activities: List[Dict[str, Any]]
    activity_summary: ActivitySummary
    recommendations: List[str]
    
class TopicProgressResponse(BaseModel):
    user_id: str
    topic: str
    proficiency: float
    confidence: float
    activities: List[Dict[str, Any]]
    concepts_mastered: List[str]
    concepts_struggling: List[str]
    
class LearningActivityRequest(BaseModel):
    user_id: str
    activity_type: str  # quiz, flashcard, tutoring
    topic: str
    details: Dict[str, Any]  # Specific details about the activity
    
class RecommendedTopic(BaseModel):
    topic: str
    reason: str
    
class RecommendedActivity(BaseModel):
    type: str
    topic: Optional[str] = None
    description: str
    
class RecommendationResponse(BaseModel):
    user_id: str
    recommended_topics: List[Dict[str, Any]]
    recommended_activities: List[Dict[str, Any]]
    focus_areas: List[str]
    daily_goal: Dict[str, Any]
    long_term_goals: List[Dict[str, Any]]
    recommendations: List[str]
    
class ReviewItem(BaseModel):
    id: str
    type: str  # flashcard, quiz_topic
    topic: str
    due_date: str
    
class SpacedRepetitionSchedule(BaseModel):
    user_id: str
    today: List[Dict[str, Any]]
    overdue: List[Dict[str, Any]]
    upcoming: Dict[str, List[Dict[str, Any]]]  # date -> items
    
class StudyPlanRequest(BaseModel):
    user_id: str
    days: Optional[int] = 7
    
class StudyPlanDayActivity(BaseModel):
    type: str
    duration: int
    description: str
    
class StudyPlanDayTopic(BaseModel):
    topic: str
    activities: List[StudyPlanDayActivity]
    total_duration: int
    
class StudyPlanDay(BaseModel):
    date: str
    day_of_week: str
    topics: List[StudyPlanDayTopic]
    total_duration: int
    
class StudyPlanResponse(BaseModel):
    user_id: str
    generated_at: str
    schedule: List[StudyPlanDay]
    weekly_goals: List[str]