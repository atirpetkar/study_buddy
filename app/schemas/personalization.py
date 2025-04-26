# app/schemas/personalization.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class LearningStyleRequest(BaseModel):
    user_id: str
    conversation_history: Optional[List[Dict[str, Any]]] = None

class LearningStyleResponse(BaseModel):
    primary_style: str
    secondary_style: Optional[str] = None
    confidence: float
    scores: Dict[str, float]
    last_updated: str

class PersonalizedQuizRequest(BaseModel):
    user_id: str
    topic: str
    difficulty: Optional[str] = None  # If None, will be determined by progress

class PersonalizedFlashcardRequest(BaseModel):
    user_id: str
    topic: str
    num_cards: Optional[int] = None  # If None, will be determined by progress

class PersonalizationResponse(BaseModel):
    learning_style: LearningStyleResponse
    strategies: List[str]

class StrategyResponse(BaseModel):
    user_id: str
    learning_style: str
    strategies: List[str]

class StudyMaterialResponse(BaseModel):
    user_id: str
    learning_style: str
    topic: str
    material_type: str  # "quiz", "flashcard", "tutorial", etc.
    content: Dict[str, Any]
    presentation_hints: List[str]