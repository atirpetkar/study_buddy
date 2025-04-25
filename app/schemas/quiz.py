# app/schemas/quiz.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QuizRequest(BaseModel):
    user_id: str
    topic: Optional[str] = None
    num_questions: int = 5
    difficulty: str = "medium"  # easy, medium, hard
    document_id: Optional[str] = None
    save_quiz: bool = True

class QuizResponse(BaseModel):
    id: str
    questions: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class QuizAttemptRequest(BaseModel):
    user_id: str
    answers: Dict[str, str]  # Map of question_id -> answer_choice

class QuizAttemptResponse(BaseModel):
    id: str
    quiz_id: str
    score: Dict[str, Any]
    feedback: str
    question_results: List[Dict[str, Any]]