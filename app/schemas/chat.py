from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    user_id: str
    message: str
    mode: str = "chat"  # chat, tutor, quiz, flashcard

class ChatResponse(BaseModel):
    response: str
    context_used: List[str] = []