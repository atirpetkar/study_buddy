# app/core/sk/skills/quiz_skill.py
from typing import Dict, Any, List
import json
import semantic_kernel as sk
# Updated imports for Semantic Kernel 1.28.1
from semantic_kernel.functions import kernel_function
from app.core.quiz_generator import QuizGenerator

class QuizSkill:
    """Semantic Kernel implementation of quiz generation functionality"""
    
    def __init__(self, kernel):
        """Initialize the quiz skill"""
        self.kernel = kernel
        self.quiz_gen = QuizGenerator()
    
    @kernel_function(
        description="Generate a quiz based on educational content",
        name="GenerateQuiz"
    )
    async def generate_quiz(self, context: str, num_questions: str = "5", 
                          difficulty: str = "medium", topic: str = None) -> str:
        """Generate a quiz using SK function format"""
        # Get the LLM service
        chat_service = self.kernel.get_service("github")
        
        # Use the existing QuizGenerator but with SK's LLM
        quiz_result = await self.quiz_gen.generate_quiz(
            context=context,
            num_questions=int(num_questions),
            difficulty=difficulty,
            topic=topic,
            client=chat_service._client,
            model_name=chat_service._ai_model_id
        )
        
        # Convert to string format for SK
        return json.dumps(quiz_result)
    
    @kernel_function(
        description="Generate a quiz response for the conversation",
        name="GenerateQuizResponse"
    )
    async def generate_quiz_response(self, input: str, context: str, history: str) -> str:
        """Generate a conversational response for quiz requests"""
        # Get chat service for LLM interactions
        chat_service = self.kernel.get_service("github")
        
        # Parse the request to determine parameters
        chat_completion = await chat_service.complete_chat_async(
            sk.ChatHistory([
                sk.ChatMessage.system_message(
                    "You are a quiz parameter extractor. Extract the parameters for quiz generation " +
                    "from the user's message. Return a JSON with num_questions, difficulty, and topic."
                ),
                sk.ChatMessage.user_message(input)
            ])
        )
        
        try:
            params = json.loads(chat_completion.result)
        except:
            # Default parameters if extraction fails
            params = {
                "num_questions": 5,
                "difficulty": "medium",
                "topic": None
            }
        
        # Generate the quiz
        quiz_result = await self.generate_quiz(
            context=context,
            num_questions=str(params.get("num_questions", 5)),
            difficulty=params.get("difficulty", "medium"),
            topic=params.get("topic")
        )
        
        # Format the response
        quiz_data = json.loads(quiz_result)
        
        response = "Here's a quiz based on the educational content:\n\n"
        
        for i, question in enumerate(quiz_data.get("questions", [])):
            response += f"Question {i+1}: {question['text']}\n"
            for letter, option in question.get("options", {}).items():
                response += f"{letter}. {option}\n"
            response += "\n"
        
        response += "Let me know when you're ready for the answers!"
        
        return response

class SKQuizGenerator(QuizGenerator):
    """SK adapter for QuizGenerator that maintains the same interface"""
    
    def __init__(self):
        """Initialize the SK quiz generator"""
        super().__init__()
        # Defer the kernel import until it's actually needed
        self.kernel = None
    
    def _ensure_kernel(self):
        """Lazy-load the kernel only when needed"""
        if self.kernel is None:
            # Import here to avoid circular dependency
            from app.core.sk.kernel_factory import get_kernel
            self.kernel = get_kernel()
    
    async def generate_quiz(self, context: str, num_questions: int = 5,
                          difficulty: str = "medium", topic: str = None,
                          client=None, model_name: str = None) -> Dict[str, Any]:
        """Generate a quiz using Semantic Kernel"""
        # Ensure kernel is loaded
        self._ensure_kernel()
        
        # Create variables for the function
        context_variables = sk.ContextVariables()
        context_variables["context"] = context
        context_variables["num_questions"] = str(num_questions)
        context_variables["difficulty"] = difficulty
        context_variables["topic"] = topic if topic else ""
        
        # Get the function
        function = self.kernel.skills.get_function("QuizSkill", "GenerateQuiz")
        
        try:
            # Execute the function
            result = await self.kernel.run_async(function, input_vars=context_variables)
            quiz_result = json.loads(str(result))
            return quiz_result
        except Exception as e:
            print(f"Error generating quiz with SK: {e}")
            # Fall back to the original implementation
            return await super().generate_quiz(
                context, num_questions, difficulty, topic, client, model_name
            )

def register_quiz_skill(kernel: sk.Kernel):
    """Register the quiz skill with the kernel"""
    skill = QuizSkill(kernel)
    kernel.add_skill(skill, skill_name="QuizSkill")