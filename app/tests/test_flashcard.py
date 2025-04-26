# test_flashcard.py - Unit tests for flashcard generation logic
import pytest
import asyncio
from app.core.flashcard_generator import FlashcardGenerator

# Use a static context for testing (excerpt from Machine Learning Fundamentals)
TEST_CONTEXT = """
Machine learning is a subfield of artificial intelligence that focuses on developing systems that can learn from and make decisions based on data. Unlike traditional programming where explicit instructions are provided, machine learning algorithms build a model based on sample data, known as training data, to make predictions or decisions without being explicitly programmed to do so.

The core objective of machine learning is to allow computers to learn automatically without human intervention and adjust actions accordingly. This capability makes machine learning particularly valuable for applications where explicit programming is difficult or infeasible, such as email filtering, computer vision, and natural language processing.

Types of Machine Learning:
- Supervised Learning: Uses labeled data to train models. Examples include classification and regression.
- Unsupervised Learning: Works with unlabeled data to find patterns. Examples include clustering and dimensionality reduction.
- Reinforcement Learning: Involves an agent learning through trial and error in an environment.
"""

@pytest.mark.asyncio
async def test_generate_flashcards_basic():
    """Test that flashcard generator produces the expected number of cards and structure."""
    generator = FlashcardGenerator()
    # The generator expects a client and model_name, but for unit test, we mock the output method
    # We'll monkeypatch the generate_flashcards method to test parsing logic only
    sample_output = """
Card 1:
Front: What is supervised learning?
Back: A type of machine learning that uses labeled data to train models, such as classification and regression tasks.

Card 2:
Front: Define unsupervised learning.
Back: A machine learning approach that works with unlabeled data to find patterns, such as clustering and dimensionality reduction.

Card 3:
Front: What is reinforcement learning?
Back: A learning paradigm where an agent learns by trial and error to maximize cumulative reward in an environment.
"""
    # Directly test the parsing logic
    cards = generator._parse_flashcards_response(sample_output)
    assert len(cards) == 3
    for card in cards:
        assert 'front' in card and 'back' in card
        assert card['front'] and card['back']

@pytest.mark.asyncio
async def test_generate_flashcards_with_context():
    """Test the full generate_flashcards method with a mock client."""
    class MockClient:
        class chat:
            class completions:
                @staticmethod
                async def create(messages, temperature, max_tokens, model):
                    class Message:
                        content = (
                            "Card 1:\nFront: What is supervised learning?\nBack: A type of machine learning that uses labeled data to train models.\n\n"
                            "Card 2:\nFront: What is unsupervised learning?\nBack: A machine learning approach that works with unlabeled data to find patterns.\n\n"
                            "Card 3:\nFront: What is reinforcement learning?\nBack: A learning paradigm where an agent learns by trial and error to maximize reward.\n"
                        )
                    class Choice:
                        message = Message()
                    class Response:
                        choices = [Choice()]
                    return Response()
    generator = FlashcardGenerator()
    result = await generator.generate_flashcards(
        context=TEST_CONTEXT,
        num_cards=3,
        topic="machine learning",
        client=MockClient(),
        model_name="mock-model"
    )
    assert 'cards' in result
    assert len(result['cards']) == 3
    for card in result['cards']:
        assert 'front' in card and 'back' in card
        assert card['front'] and card['back']

# To run: pytest test_flashcard.py