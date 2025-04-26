# app/api/personalization.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional

from app.models import db, repository
from app.schemas.personalization import (
    PersonalizationResponse,
    LearningStyleRequest,
    PersonalizedQuizRequest,
    PersonalizedFlashcardRequest,
    StrategyResponse
)
from app.core.personalization_engine import PersonalizationEngine
from app.core.quiz_generator import QuizGenerator
from app.core.flashcard_generator import FlashcardGenerator
from app.core.vector_store import get_vector_store_client
from app.core.agent import get_message_processor

router = APIRouter()
personalization_engine = PersonalizationEngine()
quiz_generator = QuizGenerator()
flashcard_generator = FlashcardGenerator()

@router.get("/learning-style/{user_id}", response_model=Dict[str, Any])
async def detect_learning_style(user_id: str, db_session = Depends(db.get_db)):
    """Detect and return user's learning style based on activity patterns"""
    try:
        vector_client = get_vector_store_client()
        processor = get_message_processor()
        
        learning_style = await personalization_engine.analyze_learning_style(
            db_session, 
            user_id
        )
        
        strategies = personalization_engine.get_learning_style_strategies(learning_style)
        
        return {
            "learning_style": learning_style,
            "strategies": strategies["recommended_strategies"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting learning style: {str(e)}")

@router.post("/quiz", response_model=Dict[str, Any])
async def generate_personalized_quiz(request: PersonalizedQuizRequest, db_session = Depends(db.get_db)):
    """Generate a personalized quiz based on learning style and progress"""
    try:
        vector_client = get_vector_store_client()
        processor = get_message_processor()
        
        quiz = await personalization_engine.generate_personalized_quiz(
            db_session,
            user_id=request.user_id,
            topic=request.topic,
            quiz_generator=quiz_generator,
            vector_client=vector_client,
            processor=processor
        )
        
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating personalized quiz: {str(e)}")

@router.post("/flashcards", response_model=Dict[str, Any])
async def generate_personalized_flashcards(request: PersonalizedFlashcardRequest, db_session = Depends(db.get_db)):
    """Generate personalized flashcards based on learning style and progress"""
    try:
        vector_client = get_vector_store_client()
        processor = get_message_processor()
        
        flashcards = await personalization_engine.generate_personalized_flashcards(
            db_session,
            user_id=request.user_id,
            topic=request.topic,
            flashcard_generator=flashcard_generator,
            vector_client=vector_client,
            processor=processor
        )
        
        return flashcards
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating personalized flashcards: {str(e)}")

@router.get("/strategies/{user_id}", response_model=StrategyResponse)
async def get_learning_strategies(user_id: str, db_session = Depends(db.get_db)):
    """Get personalized learning strategies based on detected learning style"""
    try:
        learning_style = await personalization_engine.analyze_learning_style(
            db_session, 
            user_id
        )
        
        strategies = personalization_engine.get_learning_style_strategies(learning_style)
        
        return {
            "user_id": user_id,
            "learning_style": learning_style["primary_style"],
            "strategies": strategies["recommended_strategies"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving learning strategies: {str(e)}")