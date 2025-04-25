# Update app/api/__init__.py
from fastapi import APIRouter
from app.api import user, vectorstore, chat, quiz, flashcard, progress 

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(vectorstore.router, prefix="/vectorstore", tags=["vectorstore"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(flashcard.router, prefix="/flashcard", tags=["flashcard"])  # Add this line
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])  # Add this line
