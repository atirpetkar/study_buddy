# test_day3.py
import asyncio
import os
from app.core.agent import get_message_processor
from app.core.vector_store import get_vector_store_client

async def test_chat():
    vector_client = get_vector_store_client()
    processor = get_message_processor()
    
    # Test Chat mode
    result = await processor.process_message(
        user_id="test_user",
        message="What is object-oriented programming?",
        mode="chat",
        vector_search_client=vector_client
    )
    print("\n--- CHAT MODE RESPONSE ---")
    print(result["response"])
    print("\nSources used:", result["context_used"])
    
    # Test Tutor mode
    result = await processor.process_message(
        user_id="test_user",
        message="I'm confused about inheritance in programming",
        mode="tutor",
        vector_search_client=vector_client
    )
    print("\n--- TUTOR MODE RESPONSE ---")
    print(result["response"])
    print("\nSources used:", result["context_used"])

if __name__ == "__main__":
    asyncio.run(test_chat())