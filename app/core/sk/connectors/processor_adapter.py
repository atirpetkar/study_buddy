# app/core/sk/connectors/processor_adapter.py
from typing import Dict, Any, List
import os
import json
import semantic_kernel as sk
from semantic_kernel.planners.sequential_planner import SequentialPlanner
from app.core.message_processor import MessageProcessor

class SKMessageProcessor(MessageProcessor):
    """Semantic Kernel implementation of MessageProcessor"""
    
    def __init__(self):
        """Initialize the SK message processor"""
        super().__init__()
        # Defer the kernel import until it's actually needed
        self.kernel = None
        self.planner = None
        
    def _ensure_kernel(self):
        """Lazy-load the kernel and initialize components only when needed"""
        if self.kernel is None:
            # Import here to avoid circular dependency
            from app.core.sk.kernel_factory import get_kernel
            self.kernel = get_kernel()
            # Register skills
            self._register_skills()
            # Create planner with service_id parameter for SK 1.28.1
            self.planner = SequentialPlanner(self.kernel, service_id="github")
    
    def _register_skills(self):
        """Register all required skills with the kernel"""
        # Import skills here to avoid circular imports
        from app.core.sk.skills.quiz_skill import register_quiz_skill
        from app.core.sk.skills.flashcard_skill import register_flashcard_skill
        from app.core.sk.skills.tutor_skill import register_tutor_skill
        from app.core.sk.skills.chat_skill import register_chat_skill
        
        register_quiz_skill(self.kernel)
        register_flashcard_skill(self.kernel)
        register_tutor_skill(self.kernel)
        register_chat_skill(self.kernel)
    
    async def process_message(self, user_id: str, message: str, mode: str = "chat", 
                             vector_search_client=None) -> Dict[str, Any]:
        """Process a message using Semantic Kernel"""
        # Ensure kernel is loaded and components are initialized
        self._ensure_kernel()
        
        # Get conversation history for context
        history = self.conversation_history.get(user_id, [])
        formatted_history = self._format_history(history)
        
        # Retrieve context from vector store
        search_results = None
        context = ""
        context_sources = []
        if vector_search_client:
            # Import here to avoid circular imports
            from app.utils.context_retrieval import retrieve_enhanced_context, format_context_by_source
            search_results = await retrieve_enhanced_context(vector_search_client, message)
            context, context_sources = format_context_by_source(search_results)
        
        try:
            # Use SK's planning capabilities to process the message
            # Create variables for the planner - using KernelArguments for SK 1.28.1
            from semantic_kernel.functions import KernelArguments
            arguments = KernelArguments(
                input=message,
                mode=mode,
                history=formatted_history,
                context=context,
                user_id=user_id  # Added user_id for functions that need it
            )
            
            # Create a plan and execute it
            if mode == "chat":
                function_name = "ChatSkill.GenerateResponse"
            elif mode == "tutor":
                function_name = "TutorSkill.GenerateTutoringResponse"
            elif mode == "quiz":
                function_name = "QuizSkill.GenerateQuizResponse"
            elif mode == "flashcard":
                function_name = "FlashcardSkill.GenerateFlashcardResponse"
            else:
                function_name = "ChatSkill.GenerateResponse"  # Default to chat
            
            # Get the function and execute it - updated for SK 1.28.1 API
            plugin_name, function_name = function_name.split('.')
            result = await self.kernel.invoke(
                function_name=function_name,
                plugin_name=plugin_name,
                arguments=arguments
            )
            response_text = str(result)
            
            # Update conversation history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response_text})
            
            # Keep history to a reasonable size
            if len(history) > 20:
                history = history[-20:]
            self.conversation_history[user_id] = history
            
            return {
                "response": response_text,
                "context_used": context_sources
            }
        except Exception as e:
            print(f"Error processing message with SK: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to the original implementation
            return await super().process_message(user_id, message, mode, vector_search_client)