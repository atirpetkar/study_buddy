# test_document_quiz.py
import asyncio
import os
from app.core.vector_store import get_vector_store_client
from app.core.agent import get_message_processor
from app.utils.context_retrieval import retrieve_topic_context
from app.core.quiz_generator import QuizGenerator

async def test_document_to_quiz():
    """Test full workflow from document chunks to quiz"""
    # Get dependencies
    vector_client = get_vector_store_client()
    processor = get_message_processor()
    quiz_gen = QuizGenerator()
    
    # Try different topics
    topics_to_try = [
        "machine learning",
        "supervised learning",
        "neural networks",
        "unsupervised learning"
    ]
    
    for topic in topics_to_try:
        print(f"\n===== Testing quiz generation for topic: {topic} =====")
        
        # Get enhanced context
        topic_context = await retrieve_topic_context(
            vector_client, 
            topic, 
            min_chunks=5,
            max_chunks=10
        )
        
        context = topic_context["context"]
        sources = topic_context["sources"]
        
        if not context:
            print(f"No context found for topic: {topic}")
            continue
        
        print(f"Retrieved {len(context.split())} words from {len(sources)} sources")
        
        # Generate quiz
        quiz = await quiz_gen.generate_quiz(
            context=context,
            num_questions=2,  # Keep it small for testing
            difficulty="medium",
            topic=topic,
            client=processor.client,
            model_name=processor.model_name
        )
        
        # Print results
        if quiz.get("questions"):
            print(f"Generated {len(quiz['questions'])} questions!")
            
            # Print first question as sample
            if quiz['questions']:
                sample_q = quiz['questions'][0]
                print(f"\nSample Question: {sample_q['text']}")
                for letter, option in sample_q['options'].items():
                    print(f"{letter}. {option}")
                print(f"Correct Answer: {sample_q['correct_answer']}")
        else:
            print(f"Failed to generate questions for topic: {topic}")

if __name__ == "__main__":
    asyncio.run(test_document_to_quiz())