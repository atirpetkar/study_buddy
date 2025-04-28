# app/core/sk/skills/chat_skill.py
import semantic_kernel as sk
from semantic_kernel.functions import kernel_function
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings

class ChatSkill:
    """Semantic Kernel implementation of chat functionality"""
    
    def __init__(self, kernel):
        """Initialize the chat skill"""
        self.kernel = kernel
    
    @kernel_function(
        description="Generate a response in chat mode",
        name="GenerateResponse"
    )
    async def generate_response(self, input: str, context: str, history: str) -> str:
        """Generate a conversational response"""
        # Get the LLM service
        chat_service = self.kernel.get_service("github")
        
        # Create the prompt for SK 1.28.1
        system_message = "You are Study Buddy, an AI educational assistant that helps with learning."
        user_message = f"""
        Previous conversation:
        {history}
        
        Context from relevant documents:
        {context}
        
        User: {input}
        
        Study Buddy:
        """
        
        # In SK 1.28.1, we use get_chat_message_content
        
        # Create chat history
        chat_history = ChatHistory()
        chat_history.add_system_message(system_message)
        chat_history.add_user_message(user_message)
        
        # Create settings - using PromptExecutionSettings instead of ChatRequestSettings for SK 1.28.1
        settings = PromptExecutionSettings()
        
        # Generate the response using SK 1.28.1 API
        completion = await chat_service.get_chat_message_content(chat_history, settings)
        response = completion.content if completion else "I'm sorry, I couldn't generate a response."
        
        return response

def register_chat_skill(kernel: sk.Kernel):
    """Register the chat skill with the kernel"""
    skill = ChatSkill(kernel)
    # Using add_plugin for compatibility with Semantic Kernel 1.28.1
    kernel.add_plugin(skill, plugin_name="ChatSkill")