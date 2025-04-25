# app/schemas/flashcard.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class FlashcardRequest(BaseModel):
    user_id: str
    topic: Optional[str] = None
    num_cards: int = 8
    document_id: Optional[str] = None
    save_flashcards: bool = True

class FlashcardResponse(BaseModel):
    id: str
    cards: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class FlashcardReviewRequest(BaseModel):
    user_id: str
    flashcard_id: str
    card_id: str
    confidence: int  # 1-5 rating

class FlashcardReviewResponse(BaseModel):
    success: bool
    next_review: str  # ISO date string
    recommendation: str