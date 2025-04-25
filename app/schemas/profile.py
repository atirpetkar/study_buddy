# app/schemas/profile.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ProfileCreateRequest(BaseModel):
    user_id: str
    exam_type: Optional[str] = None
    study_preferences: Optional[Dict[str, Any]] = None
    available_study_time: Optional[str] = None
    goals: Optional[List[str]] = None
    initial_topics: Optional[List[str]] = None

class ProfileUpdateRequest(BaseModel):
    exam_type: Optional[str] = None
    study_preferences: Optional[Dict[str, Any]] = None
    available_study_time: Optional[str] = None
    goals: Optional[List[str]] = None
    topics: Optional[List[str]] = None

class ProfileResponse(BaseModel):
    user_id: str
    exam_type: Optional[str] = None
    study_preferences: Optional[Dict[str, Any]] = None
    available_study_time: Optional[str] = None
    goals: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    learning_progress: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: Optional[str] = None