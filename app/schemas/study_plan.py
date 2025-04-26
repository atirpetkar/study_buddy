# app/schemas/study_plan.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class StudyActivity(BaseModel):
    type: str
    duration: int
    description: str

class StudyTopicDay(BaseModel):
    topic: str
    activities: List[StudyActivity]
    total_duration: int
    priority: Optional[str] = None
    key_concepts: Optional[List[str]] = None

class StudyPlanDay(BaseModel):
    date: str
    day_of_week: str
    topics: List[StudyTopicDay]
    total_duration: int
    style_recommendations: Optional[List[str]] = None
    suggestion: Optional[str] = None

class DocumentInsight(BaseModel):
    topic: Optional[str] = None
    type: str
    description: str
    key_concepts: Optional[List[str]] = None
    recommendation: Optional[str] = None
    recommended_activity: Optional[str] = None

class StudyPlanContent(BaseModel):
    user_id: str
    generated_at: str
    learning_style: str
    daily_study_time: int
    schedule: List[StudyPlanDay]
    weekly_goals: List[str]
    focus_areas: List[str]
    document_insights: List[DocumentInsight]

class StudyPlanResponse(BaseModel):
    plan_id: str
    plan: StudyPlanContent

class AdvancedStudyPlanRequest(BaseModel):
    user_id: str
    days: int = 7
    topic_focus: Optional[str] = None

class StudyPlanUpdateRequest(BaseModel):
    completed_activities: List[Dict[str, Any]]
    feedback: Optional[str] = None
    
class StudyPlanInsightResponse(BaseModel):
    user_id: str
    topic_recommendations: List[Dict[str, Any]]
    learning_pattern_insights: List[Dict[str, Any]]
    most_productive_times: Optional[Dict[str, Any]] = None
    completion_rate: Optional[float] = None