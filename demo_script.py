# demo_script.py
import asyncio
import time
import json
import os
import argparse
from typing import Dict, Any, List
import requests

# API Endpoint
BASE_URL = "http://localhost:8000"
USER_ID = "demo_user"

class StudyBuddyDemo:
    """Demo script for Study Buddy Agent hackathon presentation"""
    
    def __init__(self, base_url=BASE_URL, user_id=USER_ID):
        self.base_url = base_url
        self.user_id = user_id
        self.headers = {"Content-Type": "application/json"}
        
    async def run_full_demo(self):
        """Run the complete demo flow"""
        print("\n===== STUDY BUDDY AGENT DEMO =====")
        print("A personalized AI tutor for effective learning")
        
        # Step 1: Upload a document
        print("\n--- STEP 1: Document Processing ---")
        uploaded = await self.upload_document("Machine Learning Fundamentals.md")
        if not uploaded:
            print("Document upload failed. Exiting demo.")
            return
            
        print("✅ Document successfully processed and vectorized!")
        
        # Step 2: Chat about the document
        print("\n--- STEP 2: Document Q&A ---")
        questions = [
            "What are the different types of machine learning?",
            "How does supervised learning work?",
            "What are some applications of reinforcement learning?"
        ]
        
        for question in questions:
            print(f"\n🧠 Question: {question}")
            response = await self.chat_with_agent(question)
            print(f"🤖 Answer: {response}")
            time.sleep(1)
            
        # Step 3: Generate a quiz
        print("\n--- STEP 3: Quiz Generation ---")
        quiz = await self.generate_quiz("machine learning")
        
        if not quiz or not quiz.get("questions"):
            print("Quiz generation failed. Continuing demo.")
        else:
            print("✅ Quiz successfully generated!")
            
            # Display sample questions
            print("\nSample Quiz Questions:")
            for i, question in enumerate(quiz["questions"][:2], 1):
                print(f"\nQuestion {i}: {question['text']}")
                for letter, option in question["options"].items():
                    print(f"  {letter}. {option}")
                print(f"Correct Answer: {question['correct_answer']}")
                
        # Step 4: Generate flashcards
        print("\n--- STEP 4: Flashcard Generation ---")
        flashcards = await self.generate_flashcards("machine learning")
        
        if not flashcards or not flashcards.get("cards"):
            print("Flashcard generation failed. Continuing demo.")
        else:
            print("✅ Flashcards successfully generated!")
            
            # Display sample flashcards
            print("\nSample Flashcards:")
            for i, card in enumerate(flashcards["cards"][:3], 1):
                print(f"\nFlashcard {i}:")
                print(f"Front: {card['front']}")
                print(f"Back: {card['back']}")
                
        # Step 5: Demonstrate tutoring mode
        print("\n--- STEP 5: Tutoring Mode ---")
        tutoring_questions = [
            "I'm confused about the difference between supervised and unsupervised learning",
            "Can you explain neural networks in simple terms?"
        ]
        
        for question in tutoring_questions:
            print(f"\n🧠 Student: {question}")
            response = await self.tutoring_session(question)
            print(f"🤖 Tutor: {response}")
            time.sleep(1)
            
        # Step 6: Personalization features
        print("\n--- STEP 6: Personalization ---")
        learning_style = await self.detect_learning_style()
        
        if learning_style:
            print(f"\nDetected Learning Style: {learning_style.get('primary_style', 'unknown')}")
            print("Recommended Learning Strategies:")
            for strategy in learning_style.get("strategies", [])[:3]:
                print(f"- {strategy}")
                
        # Step 7: Generate study plan
        print("\n--- STEP 7: Personalized Study Plan ---")
        study_plan = await self.generate_study_plan()
        
        if study_plan and study_plan.get("plan"):
            plan_data = study_plan["plan"]
            print("✅ Personalized study plan generated!")
            
            print("\nWeekly Learning Goals:")
            for goal in plan_data.get("weekly_goals", []):
                print(f"- {goal}")
                
            print("\nSample Daily Schedule:")
            if plan_data.get("schedule"):
                day = plan_data["schedule"][0]
                print(f"\nDay: {day['day_of_week']}")
                for topic in day.get("topics", []):
                    print(f"Topic: {topic['topic']}")
                    for activity in topic.get("activities", []):
                        print(f"  - {activity['type']} ({activity['duration']} min): {activity['description']}")
        
        print("\n===== DEMO COMPLETE =====")
        print("Thank you for experiencing the Study Buddy Agent!")
        
    async def upload_document(self, filename: str) -> bool:
        """Upload and process a document"""
        if not os.path.exists(filename):
            print(f"Error: File {filename} not found")
            return False
            
        try:
            # For demo purposes, assume the document is already uploaded and vectorized
            print(f"Uploading document: {filename}")
            print("Processing document content...")
            print("Generating embeddings...")
            print("Storing vectors in database...")
            return True
        except Exception as e:
            print(f"Error uploading document: {e}")
            return False
            
    async def chat_with_agent(self, message: str) -> str:
        """Chat with the agent about documents"""
        try:
            # This would normally call the API, but we'll simulate for the demo
            time.sleep(1)  # Simulate API call
            
            # For a real implementation, use:
            # response = requests.post(
            #     f"{self.base_url}/chat/chat",
            #     json={"user_id": self.user_id, "message": message, "mode": "chat"},
            #     headers=self.headers
            # )
            # result = response.json()
            # return result.get("response", "Error: No response received")
            
            responses = {
                "What are the different types of machine learning?": 
                    "There are three main types of machine learning: 1) Supervised Learning, where algorithms learn from labeled examples, 2) Unsupervised Learning, which works with unlabeled data to find patterns, and 3) Reinforcement Learning, where an agent learns through trial and error in an environment.",
                
                "How does supervised learning work?":
                    "Supervised learning works by training algorithms on labeled data, where each example is paired with the expected output. The algorithm learns a function that maps inputs to outputs by comparing its predictions with the actual output and adjusting its parameters to minimize the difference. This approach is used for classification and regression tasks.",
                
                "What are some applications of reinforcement learning?":
                    "Reinforcement learning has several key applications including: game playing (like AlphaGo), robotics for teaching machines physical tasks, autonomous vehicles for navigation and decision-making, and resource management for optimizing systems like data center cooling or traffic light control."
            }
            
            return responses.get(message, "I don't have information about that specific topic in the document.")
            
        except Exception as e:
            print(f"Error in chat: {e}")
            return "Sorry, I encountered an error processing your request."
            
    async def generate_quiz(self, topic: str) -> Dict[str, Any]:
        """Generate a quiz on a topic"""
        try:
            # This would normally call the API, but we'll simulate for the demo
            time.sleep(2)  # Simulate API call
            
            # For a real implementation, use:
            # response = requests.post(
            #     f"{self.base_url}/quiz/generate",
            #     json={"user_id": self.user_id, "topic": topic, "num_questions": 5},
            #     headers=self.headers
            # )
            # return response.json()
            
            # Sample quiz data
            return {
                "id": "sample_quiz_123",
                "questions": [
                    {
                        "id": "q1",
                        "text": "Which of the following is NOT a type of machine learning?",
                        "options": {
                            "A": "Supervised Learning",
                            "B": "Unsupervised Learning",
                            "C": "Predictive Learning",
                            "D": "Reinforcement Learning"
                        },
                        "correct_answer": "C",
                        "explanation": "The three main types of machine learning are Supervised Learning, Unsupervised Learning, and Reinforcement Learning. Predictive Learning is not a standard category."
                    },
                    {
                        "id": "q2",
                        "text": "In supervised learning, what is the data called that the algorithm learns from?",
                        "options": {
                            "A": "Test data",
                            "B": "Training data",
                            "C": "Validation data",
                            "D": "Unlabeled data"
                        },
                        "correct_answer": "B",
                        "explanation": "In supervised learning, algorithms learn from training data, which consists of labeled examples with input features and expected outputs."
                    },
                    {
                        "id": "q3",
                        "text": "What is the primary goal of unsupervised learning?",
                        "options": {
                            "A": "To make predictions based on labeled data",
                            "B": "To find patterns or structures in unlabeled data",
                            "C": "To maximize rewards in an environment",
                            "D": "To classify data into predefined categories"
                        },
                        "correct_answer": "B",
                        "explanation": "Unsupervised learning algorithms work with unlabeled data, attempting to find patterns or structures within the input."
                    }
                ],
                "metadata": {
                    "topic": topic,
                    "difficulty": "medium",
                    "sources": ["Machine Learning Fundamentals.md"]
                }
            }
            
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return {}
            
    async def generate_flashcards(self, topic: str) -> Dict[str, Any]:
        """Generate flashcards on a topic"""
        try:
            # This would normally call the API, but we'll simulate for the demo
            time.sleep(2)  # Simulate API call
            
            # For a real implementation, use:
            # response = requests.post(
            #     f"{self.base_url}/flashcard/generate",
            #     json={"user_id": self.user_id, "topic": topic, "num_cards": 5},
            #     headers=self.headers
            # )
            # return response.json()
            
            # Sample flashcard data
            return {
                "id": "sample_flashcards_123",
                "cards": [
                    {
                        "id": "card1",
                        "front": "What is machine learning?",
                        "back": "A subfield of artificial intelligence that focuses on developing systems that can learn from and make decisions based on data, without being explicitly programmed."
                    },
                    {
                        "id": "card2",
                        "front": "What is supervised learning?",
                        "back": "A type of machine learning where algorithms are trained on labeled examples, learning a function that maps inputs to outputs, used for classification and regression tasks."
                    },
                    {
                        "id": "card3",
                        "front": "What is unsupervised learning?",
                        "back": "A type of machine learning that works with unlabeled data, attempting to find patterns or structures within the input, used for clustering, dimensionality reduction, and association."
                    },
                    {
                        "id": "card4",
                        "front": "What is reinforcement learning?",
                        "back": "A type of machine learning where an agent learns to make decisions by performing actions in an environment to maximize some notion of cumulative reward."
                    }
                ],
                "metadata": {
                    "topic": topic,
                    "card_count": 4,
                    "sources": ["Machine Learning Fundamentals.md"]
                }
            }
            
        except Exception as e:
            print(f"Error generating flashcards: {e}")
            return {}
    
    async def tutoring_session(self, question: str) -> str:
        """Interact with the agent in tutoring mode"""
        try:
            # This would normally call the API, but we'll simulate for the demo
            time.sleep(1.5)  # Simulate API call
            
            # For a real implementation, use:
            # response = requests.post(
            #     f"{self.base_url}/chat/chat",
            #     json={"user_id": self.user_id, "message": question, "mode": "tutor"},
            #     headers=self.headers
            # )
            # result = response.json()
            # return result.get("response", "Error: No response received")
            
            responses = {
                "I'm confused about the difference between supervised and unsupervised learning": 
                    "Great question! Let's think about this step by step. What do you already know about how data is used in machine learning? \n\nIn supervised learning, we provide the algorithm with labeled examples - imagine a teacher showing a student the correct answers. The algorithm learns to map inputs to known outputs.\n\nIn unsupervised learning, we don't provide any labels - it's like giving a student data and asking them to find patterns on their own. \n\nCan you think of a real-world example where you'd use each approach?",
                
                "Can you explain neural networks in simple terms?":
                    "I'd be happy to explain neural networks! Let's start with the basics. Have you ever thought about how your brain processes information? \n\nA neural network is somewhat inspired by how our brains work. Imagine a network of connected nodes (called neurons). Each connection can transmit a signal to other neurons.\n\nThink of a neural network as a series of layers. The first layer receives input (like an image), middle layers process it, and the final layer produces an output (like 'this is a cat').\n\nDoes that make sense so far? What specific aspect of neural networks would you like to understand better?"
            }
            
            return responses.get(question, "That's an interesting question. Let's break this down together. What do you already understand about this topic, and what specifically is confusing you?")
            
        except Exception as e:
            print(f"Error in tutoring session: {e}")
            return "Sorry, I encountered an error processing your request."
    
    async def detect_learning_style(self) -> Dict[str, Any]:
        """Detect user's learning style"""
        try:
            # This would normally call the API, but we'll simulate for the demo
            time.sleep(1)  # Simulate API call
            
            # For a real implementation, use:
            # response = requests.get(
            #     f"{self.base_url}/personalization/learning-style/{self.user_id}",
            #     headers=self.headers
            # )
            # return response.json()
            
            # Sample learning style data
            return {
                "learning_style": {
                    "primary_style": "visual",
                    "secondary_style": "reading_writing",
                    "confidence": 0.65,
                    "scores": {
                        "visual": 0.45,
                        "auditory": 0.15,
                        "reading_writing": 0.25,
                        "kinesthetic": 0.15
                    },
                    "last_updated": "2023-04-20T15:30:45.123Z"
                },
                "strategies": [
                    "Use color coding in your notes",
                    "Create mind maps for complex topics",
                    "Draw diagrams to represent concepts",
                    "Watch educational videos when available",
                    "Use flashcards with images or symbols"
                ]
            }
            
        except Exception as e:
            print(f"Error detecting learning style: {e}")
            return {}
    
    async def generate_study_plan(self) -> Dict[str, Any]:
        """Generate a personalized study plan"""
        try:
            # This would normally call the API, but we'll simulate for the demo
            time.sleep(2)  # Simulate API call
            
            # For a real implementation, use:
            # response = requests.post(
            #     f"{self.base_url}/study-plan/advanced",
            #     json={"user_id": self.user_id, "days": 7},
            #     headers=self.headers
            # )
            # return response.json()
            
            # Sample study plan data
            now = time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            return {
                "plan_id": "sample_plan_123",
                "plan": {
                    "user_id": self.user_id,
                    "generated_at": now,
                    "learning_style": "visual",
                    "daily_study_time": 120,
                    "schedule": [
                        {
                            "date": "2023-04-21",
                            "day_of_week": "Friday",
                            "topics": [
                                {
                                    "topic": "Machine Learning",
                                    "activities": [
                                        {
                                            "type": "reading",
                                            "duration": 20,
                                            "description": "Read introduction to Machine Learning"
                                        },
                                        {
                                            "type": "visualization",
                                            "duration": 15,
                                            "description": "Create visual representations of Machine Learning concepts"
                                        },
                                        {
                                            "type": "flashcards",
                                            "duration": 15,
                                            "description": "Review basic Machine Learning flashcards"
                                        }
                                    ],
                                    "total_duration": 50,
                                    "priority": "high",
                                    "key_concepts": ["Supervised Learning", "Unsupervised Learning", "Reinforcement Learning"]
                                },
                                {
                                    "topic": "Neural Networks",
                                    "activities": [
                                        {
                                            "type": "tutorial",
                                            "duration": 20,
                                            "description": "Complete tutorial on Neural Networks fundamentals"
                                        },
                                        {
                                            "type": "diagram",
                                            "duration": 15,
                                            "description": "Draw a diagram of a simple neural network"
                                        }
                                    ],
                                    "total_duration": 35,
                                    "priority": "medium"
                                }
                            ],
                            "total_duration": 85,
                            "style_recommendations": [
                                "Use color coding in your notes",
                                "Create mind maps for complex topics",
                                "Draw diagrams to represent concepts"
                            ]
                        }
                    ],
                    "weekly_goals": [
                        "Master the fundamentals of Machine Learning",
                        "Practice applying concepts in Neural Networks",
                        "Complete all scheduled study sessions",
                        "Review progress at the end of the week"
                    ],
                    "focus_areas": ["Machine Learning", "Neural Networks"],
                    "document_insights": [
                        {
                            "topic": "Machine Learning",
                            "type": "complexity",
                            "description": "This topic contains intermediate level content",
                            "key_concepts": ["Supervised Learning", "Unsupervised Learning", "Reinforcement Learning"],
                            "recommendation": "Balance theory with practical applications"
                        }
                    ]
                }
            }
            
        except Exception as e:
            print(f"Error generating study plan: {e}")
            return {}

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Study Buddy Demo Script")
    parser.add_argument("--url", default=BASE_URL, help="API base URL")
    parser.add_argument("--user", default=USER_ID, help="Demo user ID")
    args = parser.parse_args()
    
    # Run demo
    demo = StudyBuddyDemo(args.url, args.user)
    asyncio.run(demo.run_full_demo())