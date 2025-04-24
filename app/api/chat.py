from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.core.agent import study_buddy_agent
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.vector_store import get_vector_store_client

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message from the user and return a response from the agent.
    """
    # Get vector store client for context retrieval
    vector_client = get_vector_store_client()
    
    # Process the message
    result = await study_buddy_agent.process_message(
        user_id=request.user_id,
        message=request.message,
        mode=request.mode,
        vector_search_client=vector_client
    )
    
    return ChatResponse(
        response=result["response"],
        context_used=result["context_used"]
    )