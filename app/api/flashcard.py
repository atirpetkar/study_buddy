# app/api/flashcard.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
import uuid

from app.core.vector_store import get_vector_store_client
from app.core.agent import get_message_processor
from app.core.flashcard_generator import FlashcardGenerator
from app.utils.context_retrieval import retrieve_enhanced_context, format_context_by_source, retrieve_topic_context
from app.models import db, repository
from app.schemas.flashcard import FlashcardRequest, FlashcardResponse, FlashcardReviewRequest, FlashcardReviewResponse

router = APIRouter()
flashcard_generator = FlashcardGenerator()

@router.post("/generate", response_model=FlashcardResponse)
async def generate_flashcards(request: FlashcardRequest, db_session = Depends(db.get_db)):
    """Generate flashcards based on document content"""
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
                doc_content = repository.get_document_content(db_session, request.document_id)
                if doc_content:
                    context = doc_content
                    context_sources = [request.document_id]
        
        if not context:
            raise HTTPException(status_code=400, detail="Could not find relevant content for flashcard generation")
        
        # Generate flashcards
        flashcard_result = await flashcard_generator.generate_flashcards(
            context=context,
            num_cards=request.num_cards,
            topic=request.topic,
            client=processor.client,
            model_name=processor.model_name
        )
        
        if "error" in flashcard_result and flashcard_result["error"]:
            raise HTTPException(status_code=500, detail=flashcard_result["error"])
        
        # Add sources to flashcard metadata
        flashcard_result["metadata"]["sources"] = context_sources
        
        # Save flashcards to database if requested
        if request.save_flashcards:
            flashcard_db = repository.create_flashcards(
                db_session, 
                user_id=request.user_id,
                document_id=request.document_id if request.document_id else context_sources[0] if context_sources else "unknown",
                flashcard_content=flashcard_result
            )
            flashcard_result["id"] = flashcard_db.id
        else:
            flashcard_result["id"] = "temp_" + str(uuid.uuid4())
        
        return FlashcardResponse(
            id=flashcard_result["id"],
            cards=flashcard_result["cards"],
            metadata=flashcard_result["metadata"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating flashcards: {str(e)}")

@router.post("/review", response_model=FlashcardReviewResponse)
async def submit_flashcard_review(request: FlashcardReviewRequest, db_session = Depends(db.get_db)):
    """Submit a flashcard review with confidence rating"""
    try:
        # Record the review
        review = repository.record_flashcard_review(
            db_session,
            flashcard_id=request.flashcard_id,
            user_id=request.user_id,
            confidence=request.confidence
        )
        
        # Generate recommendation based on confidence
        recommendation = ""
        if request.confidence <= 2:
            recommendation = "You should review this concept again soon. Consider creating a more detailed note on this topic."
        elif request.confidence == 3:
            recommendation = "You're making progress with this concept. Regular review will help solidify your understanding."
        else:
            recommendation = "You seem to have a good grasp of this concept. Keep up the good work!"
        
        return FlashcardReviewResponse(
            success=True,
            next_review=review.next_review_at.isoformat(),
            recommendation=recommendation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing flashcard review: {str(e)}")

@router.get("/due/{user_id}", response_model=List[FlashcardResponse])
async def get_due_flashcards(user_id: str, db_session = Depends(db.get_db)):
    """Get flashcards that are due for review"""
    try:
        due_flashcards = repository.get_flashcards_due_for_review(db_session, user_id)
        
        return [
            FlashcardResponse(
                id=flashcard["id"],
                cards=flashcard["content"]["cards"],
                metadata=flashcard["content"].get("metadata", {})
            ) 
            for flashcard in due_flashcards
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving due flashcards: {str(e)}")

@router.get("/{flashcard_id}", response_model=FlashcardResponse)
async def get_flashcards(flashcard_id: str, db_session = Depends(db.get_db)):
    """Get flashcards by ID"""
    try:
        flashcard = repository.get_flashcards(db_session, flashcard_id)
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcards not found")
        
        return FlashcardResponse(
            id=flashcard["id"],
            cards=flashcard["content"]["cards"],
            metadata=flashcard["content"].get("metadata", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving flashcards: {str(e)}")