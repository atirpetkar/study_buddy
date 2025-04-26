# app/core/sk/skills/flashcard_skill.py
from typing import Dict, Any, List
import json
import semantic_kernel as sk
from semantic_kernel.skill_definition import sk_function, sk_function_context_parameter
from app.core.flashcard_generator import FlashcardGenerator

class FlashcardSkill:
    """Semantic Kernel implementation of flashcard generation functionality"""
    
    def __init__(self, kernel):
        """Initialize the flashcard skill"""
        self.kernel = kernel
        self.flashcard_gen = FlashcardGenerator()
    
    @sk_function(
        description="Generate flashcards based on educational content",
        name="GenerateFlashcards"
    )
    @sk_function_context_parameter(
        name="context",
        description="Educational content to generate flashcards from"
    )
    @sk_function_context_parameter(
        name="num_cards",
        description="Number of flashcards to generate",
        default_value="8"
    )
    @sk_function_context_parameter(
        name="topic",
        description="Topic of the flashcards",
        default_value=None
    )
    async def generate_flashcards(self, context: str, num_cards: str = "8", 
                                topic: str = None) -> str:
        """Generate flashcards using SK function format"""
        # Get the LLM service
        chat_service = self.kernel.get_service("github")
        
        # Use the existing FlashcardGenerator but with SK's LLM
        flashcard_result = await self.flashcard_gen.generate_flashcards(
            context=context,
            num_cards=int(num_cards),
            topic=topic,
            client=chat_service._client,
            model_name=chat_service._ai_model_id
        )
        
        # Convert to string format for SK
        return json.dumps(flashcard_result)
    
    @sk_function(
        description="Generate a flashcard response for the conversation",
        name="GenerateFlashcardResponse"
    )
    @sk_function_context_parameter(
        name="input",
        description="User's input message"
    )
    @sk_function_context_parameter(
        name="context",
        description="Retrieved context about the topic"
    )
    @sk_function_context_parameter(
        name="history",
        description="Conversation history"
    )
    async def generate_flashcard_response(self, input: str, context: str, history: str) -> str:
        """Generate a conversational response for flashcard requests"""
        # Get chat service for LLM interactions
        chat_service = self.kernel.get_service("github")
        
        # Parse the request to determine parameters
        chat_completion = await chat_service.complete_chat_async(
            sk.ChatHistory([
                sk.ChatMessage.system_message(
                    "You are a flashcard parameter extractor. Extract the parameters for flashcard generation " +
                    "from the user's message. Return a JSON with num_cards and topic."
                ),
                sk.ChatMessage.user_message(input)
            ])
        )
        
        try:
            params = json.loads(chat_completion.result)
        except:
            # Default parameters if extraction fails
            params = {
                "num_cards": 8,
                "topic": None
            }
        
        # Generate the flashcards
        flashcard_result = await self.generate_flashcards(
            context=context,
            num_cards=str(params.get("num_cards", 8)),
            topic=params.get("topic")
        )
        
        # Format the response
        flashcard_data = json.loads(flashcard_result)
        
        response = "Here are some flashcards based on the educational content:\n\n"
        
        for i, card in enumerate(flashcard_data.get("cards", [])):
            response += f"Flashcard {i+1}:\n"
            response += f"Front: {card.get('front', '')}\n"
            response += f"Back: {card.get('back', '')}\n\n"
        
        response += "Would you like to review these flashcards?"
        
        return response

class SKFlashcardGenerator(FlashcardGenerator):
    """SK adapter for FlashcardGenerator that maintains the same interface"""
    
    def __init__(self):
        """Initialize the SK flashcard generator"""
        super().__init__()
        # Get the kernel
        from app.core.sk.kernel_factory import get_kernel
        self.kernel = get_kernel()
    
    async def generate_flashcards(self, context: str, num_cards: int = 8,
                                topic: str = None, client=None, 
                                model_name: str = None) -> Dict[str, Any]:
        """Generate flashcards using Semantic Kernel"""
        # Create variables for the function
        context_variables = sk.ContextVariables()
        context_variables["context"] = context
        context_variables["num_cards"] = str(num_cards)
        context_variables["topic"] = topic if topic else ""
        
        # Get the function
        function = self.kernel.skills.get_function("FlashcardSkill", "GenerateFlashcards")
        
        try:
            # Execute the function
            result = await self.kernel.run_async(function, input_vars=context_variables)
            flashcard_result = json.loads(str(result))
            return flashcard_result
        except Exception as e:
            print(f"Error generating flashcards with SK: {e}")
            # Fall back to the original implementation
            return await super().generate_flashcards(
                context, num_cards, topic, client, model_name
            )

def register_flashcard_skill(kernel: sk.Kernel):
    """Register the flashcard skill with the kernel"""
    skill = FlashcardSkill(kernel)
    kernel.add_skill(skill, skill_name="FlashcardSkill")