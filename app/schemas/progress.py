# app/schemas/progress.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ProgressUpdateRequest(BaseModel):
    user_id: str
    topic: str
    activity_type: str  # quiz, flashcard, chat
    performance: float  # 0-1 score
    confidence: Optional[float] = None  # 0-1 self-reported confidence

class ProgressResponse(BaseModel):
    user_id: str
    overall_proficiency: float
    overall_confidence: float
    topics: Dict[str, Any]
    topics_count: int

class RecommendationsResponse(BaseModel):
    recommendations: List[str]
    focus_topics: List[str]
    review_topics: List[str]