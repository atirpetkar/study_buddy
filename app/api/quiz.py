# app/api/quiz.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
import uuid

from app.core.vector_store import get_vector_store_client
from app.core.agent import get_message_processor
from app.core.quiz_generator import QuizGenerator
from app.core.quiz_attempt import QuizScorer
from app.utils.context_retrieval import retrieve_enhanced_context, format_context_by_source, retrieve_topic_context
from app.models import db, repository
from app.schemas.quiz import QuizRequest, QuizResponse, QuizAttemptRequest, QuizAttemptResponse

import json

router = APIRouter()
quiz_generator = QuizGenerator()
quiz_scorer = QuizScorer()

# Update the generate_quiz function in app/api/quiz.py
@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest, db_session = Depends(db.get_db)):
    """Generate a quiz based on document content"""
    try:
        # Get vector store client
        vector_client = get_vector_store_client()
        
        # Get message processor for LLM access
        processor = get_message_processor()
        
        # Get enhanced topic context
        topic = request.topic if request.topic else "key concepts"
        topic_context = await retrieve_topic_context(
            vector_client, 
            topic, 
            min_chunks=8,
            max_chunks=15
        )
        
        context = topic_context["context"]
        context_sources = topic_context["sources"]
        
        if not context:
            # Try direct document retrieval as fallback
            if request.document_id:
                # Get document from DB
                # This is a placeholder - you'll need to implement this
                doc_content = "Document content would be here"
                context = doc_content
                context_sources = [request.document_id]
        
        if not context:
            raise HTTPException(status_code=400, detail="Could not find relevant content for quiz generation")
        
        # Generate quiz
        quiz_result = await quiz_generator.generate_quiz(
            context=context,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            topic=request.topic,
            client=processor.client,
            model_name=processor.model_name
        )
        
        if "error" in quiz_result and quiz_result["error"]:
            raise HTTPException(status_code=500, detail=quiz_result["error"])
        
        # Add sources to quiz metadata
        quiz_result["metadata"]["sources"] = context_sources
        
        # Save quiz to database if requested
        if request.save_quiz:
            quiz_db = repository.create_quiz(
                db_session, 
                user_id=request.user_id,
                document_id=request.document_id if request.document_id else context_sources[0] if context_sources else "unknown",
                quiz_content=quiz_result
            )
            quiz_result["id"] = quiz_db.id
        
        return QuizResponse(
            id=quiz_result.get("id", "temp_" + str(uuid.uuid4())),
            questions=quiz_result["questions"],
            metadata=quiz_result["metadata"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")
    
@router.post("/attempt/{quiz_id}", response_model=QuizAttemptResponse)
async def submit_quiz_attempt(quiz_id: str, request: QuizAttemptRequest, db_session = Depends(db.get_db)):
    """Submit and score a quiz attempt"""
    try:
        # Get the quiz
        quiz = repository.get_quiz(db_session, quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Score the attempt
        results = quiz_scorer.score_attempt(quiz["content"], request.answers)
        
        # Save the attempt
        attempt = repository.save_quiz_attempt(
            db_session,
            quiz_id=quiz_id,
            user_id=request.user_id,
            answers=request.answers,
            score=results["score"]["percentage"]
        )
        
        # Update student progress
        if quiz["content"].get("metadata", {}).get("topic"):
            topic = quiz["content"]["metadata"]["topic"]
            repository.update_progress(
                db_session,
                user_id=request.user_id,
                topic=topic,
                results=results
            )
        
        return QuizAttemptResponse(
            id=results["attempt_id"],
            quiz_id=quiz_id,
            score=results["score"],
            feedback=results["feedback"],
            question_results=results["question_results"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing quiz attempt: {str(e)}")

@router.get("/history/{user_id}", response_model=List[Dict[str, Any]])
async def get_quiz_history(user_id: str, db_session = Depends(db.get_db)):
    """Get quiz history for a user"""
    try:
        attempts = repository.get_quiz_attempts(db_session, user_id)
        return attempts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving quiz history: {str(e)}")

@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: str, db_session = Depends(db.get_db)):
    """Get a quiz by ID"""
    try:
        quiz = repository.get_quiz(db_session, quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        return QuizResponse(
            id=quiz["id"],
            questions=quiz["content"]["questions"],
            metadata=quiz["content"].get("metadata", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving quiz: {str(e)}")