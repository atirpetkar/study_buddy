# app/api/__init__.py
from fastapi import APIRouter
from app.api import user, vectorstore, chat, quiz, flashcard, progress, learning_progress, personalization, study_plan

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(vectorstore.router, prefix="/vectorstore", tags=["vectorstore"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(flashcard.router, prefix="/flashcard", tags=["flashcard"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(learning_progress.router, prefix="/learning", tags=["learning"])
api_router.include_router(personalization.router, prefix="/personalization", tags=["personalization"])
api_router.include_router(study_plan.router, prefix="/study-plan", tags=["study_plan"])