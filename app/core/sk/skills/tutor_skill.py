# app/core/sk/skills/tutor_skill.py
from typing import Dict, Any, List
import semantic_kernel as sk
# Updated imports for Semantic Kernel 1.28.1
from semantic_kernel.functions import kernel_function
from app.core.tutoring import TutoringSessionManager

class TutorSkill:
    """Semantic Kernel implementation of tutoring functionality"""
    
    def __init__(self, kernel):
        """Initialize the tutor skill"""
        self.kernel = kernel
        self.tutor_manager = TutoringSessionManager()
    
    @kernel_function(
        description="Generate a tutoring response using the Socratic method",
        name="GenerateTutoringResponse"
    )
    async def generate_tutoring_response(self, input: str, context: str, 
                                      history: str, user_id: str = "default_user") -> str:
        """Generate a tutoring response using the Socratic method"""
        # Get the tutoring session
        session = self.tutor_manager.get_session(user_id)
        
        # Add session context to the prompt
        session_context = session.format_session_context()
        full_context = context + "\n\n" + session_context if context else session_context
        
        # Create the prompt
        prompt = f"""
        You are Study Buddy in Tutor Mode, an expert tutor who uses the Socratic method to guide students toward understanding.

        Your tutoring follows this structured approach:
        1. IDENTIFY: Understand what the student knows and doesn't know
        2. QUESTION: Ask targeted questions to lead them toward discovery
        3. GUIDE: Provide hints and partial explanations when needed
        4. VALIDATE: Confirm understanding before moving to the next concept
        5. CONNECT: Link new knowledge to previously understood concepts

        Previous conversation:
        {history}

        Context from relevant documents:
        {full_context}

        Student: {input}

        Study Buddy (Tutor Mode):
        """
        
        # Get the LLM service
        chat_service = self.kernel.get_service("github")
        
        # Generate the response
        chat_history = sk.ChatHistory()
        chat_history.add_system_message(
            "You are Study Buddy in Tutor Mode, an expert tutor who uses the Socratic method."
        )
        chat_history.add_user_message(prompt)
        
        completion = await chat_service.complete_chat_async(chat_history)
        response = completion.result
        
        # Update tutoring session
        session.analyze_response(response)
        
        return response

class SKTutoringManager(TutoringSessionManager):
    """SK adapter for TutoringSessionManager that maintains the same interface"""
    
    def __init__(self):
        """Initialize the SK tutoring manager"""
        super().__init__()
        # Defer the kernel import until it's actually needed
        self.kernel = None
    
    def _ensure_kernel(self):
        """Lazy-load the kernel only when needed"""
        if self.kernel is None:
            # Import here to avoid circular dependency
            from app.core.sk.kernel_factory import get_kernel
            self.kernel = get_kernel()

def register_tutor_skill(kernel: sk.Kernel):
    """Register the tutor skill with the kernel"""
    skill = TutorSkill(kernel)
    kernel.add_skill(skill, skill_name="TutorSkill")