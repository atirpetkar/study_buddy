# app/schemas/chat.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    user_id: str
    message: str
    mode: str = "chat"  # chat, tutor, quiz, flashcard

class ChatResponse(BaseModel):
    response: str
    context_used: List[str] = []

class ConversationEntry(BaseModel):
    message: str
    response: str
    timestamp: str
    sources: List[str] = []

class ConversationHistoryResponse(BaseModel):
    history: List[ConversationEntry] = []