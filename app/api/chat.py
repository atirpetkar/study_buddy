# app/api/chat.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List

from app.core.agent import get_message_processor
from app.schemas.chat import ChatRequest, ChatResponse, ConversationHistoryResponse
from app.core.vector_store import get_vector_store_client
from app.models import db, repository

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db_session = Depends(db.get_db)):
    """
    Process a chat message from the user and return a response from the agent.
    """
    # Get vector store client for context retrieval
    vector_client = get_vector_store_client()
    
    # Get message processor
    processor = get_message_processor()
    
    # Process the message
    result = await processor.process_message(
        user_id=request.user_id,
        message=request.message,
        mode=request.mode,
        vector_search_client=vector_client
    )
    
    # Save conversation to database in background
    try:
        # Save the conversation to database
        repository.save_conversation(
            db_session,
            user_id=request.user_id,
            message=request.message,
            response=result["response"],
            sources=result["context_used"]
        )
    except Exception as e:
        # Log but don't fail the request
        print(f"Error saving conversation: {e}")
    
    return ChatResponse(
        response=result["response"],
        context_used=result["context_used"]
    )

@router.get("/history/{user_id}", response_model=ConversationHistoryResponse)
async def get_history(user_id: str, limit: int = 20, db_session = Depends(db.get_db)):
    """
    Get conversation history for a user.
    """
    try:
        # Get conversation history from DB
        history = repository.get_user_conversations(db_session, user_id, limit)
        return ConversationHistoryResponse(
            history=[{
                "message": h.message,
                "response": h.response,
                "timestamp": h.created_at.isoformat(),
                "sources": h.source.split(", ") if h.source else []
            } for h in history]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")