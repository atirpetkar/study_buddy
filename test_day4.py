# test_quiz_final.py
import asyncio
import os
from app.core.quiz_generator import QuizGenerator
from app.core.agent import get_message_processor

async def test_simple_quiz():
    """Test quiz generation with a very simple context"""
    processor = get_message_processor()
    quiz_gen = QuizGenerator()
    
    # Simple test context
    simple_test_context = """
Machine Learning Basics:

Machine learning is a field of artificial intelligence that uses algorithms to learn from data.

There are three main types of machine learning:
1. Supervised Learning: Uses labeled data to train models. Examples include classification and regression.
2. Unsupervised Learning: Works with unlabeled data to find patterns. Examples include clustering and dimensionality reduction.
3. Reinforcement Learning: Involves an agent learning through trial and error in an environment.

Key machine learning algorithms include:
- Linear Regression for predicting continuous values
- Decision Trees for classification and regression
- K-means for clustering similar data points
- Support Vector Machines for classification tasks

The machine learning process involves:
- Data collection and preparation
- Model selection and training
- Evaluation using metrics like accuracy or error rates
- Deployment and monitoring
    """
    
    try:
        print("Generating quiz with simple test context...")
        quiz = await quiz_gen.generate_quiz(
            context=simple_test_context,
            num_questions=3,
            difficulty="easy",
            topic="machine learning basics",
            client=processor.client,
            model_name=processor.model_name
        )
        
        print("\n--- GENERATED QUIZ ---")
        if quiz.get("questions"):
            print(f"Successfully generated {len(quiz['questions'])} questions!")
            
            # Print all questions
            for i, q in enumerate(quiz["questions"]):
                print(f"\nQuestion {i+1}: {q['text']}")
                for letter, option in q['options'].items():
                    print(f"{letter}. {option}")
                print(f"Correct Answer: {q['correct_answer']}")
                if 'explanation' in q:
                    print(f"Explanation: {q['explanation']}")
        else:
            print("No questions were generated. Error:", quiz.get("error", "Unknown error"))
    
    except Exception as e:
        import traceback
        print(f"Error in quiz test: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_quiz())