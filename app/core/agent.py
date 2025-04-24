import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
import os
from typing import List, Dict, Any
import asyncio
import json

class StudyBuddyAgent:
    def __init__(self):
        self.kernel = self._setup_kernel()
        self.conversation_history = {}  # Simple in-memory storage for now
        
    def _setup_kernel(self):
        """Initialize the Semantic Kernel with the GitHub model"""
        kernel = sk.Kernel()
        
        # Configure for GitHub model
        model_id = os.getenv("GITHUB_MODEL", "gpt-4o")
        api_key = os.environ.get("GITHUB_TOKEN")
        endpoint = "https://models.github.ai/inference"
        
        try:
            kernel.add_service(
                OpenAIChatCompletion(
                    service_id="github-chat",
                    api_key=api_key
                )
            )
            print(f"Successfully added GitHub model {model_id} as a service")
        except Exception as e:
            print(f"Error setting up GitHub model service: {e}")
        
        # Import semantic skills (prompt templates)
        skills_directory = os.path.join(os.path.dirname(__file__), "..", "skills")
        try:
            # First try to import as semantic skills (prompt templates)
            print(f"Loading skills from {skills_directory}")
            self.study_buddy_skills = kernel.import_semantic_skill_from_directory(
                skills_directory, "StudyBuddy"
            )
            print(f"Loaded skills: {list(self.study_buddy_skills.keys())}")
        except Exception as e:
            print(f"Error loading semantic skills: {e}")
            self.study_buddy_skills = {}
            
            # Create plugin functions with inline prompts as backup
            if not self.study_buddy_skills:
                print("Creating inline prompt functions")
                from semantic_kernel.functions import kernel_function

                @kernel_function
                async def chat(input: str, history: str, context: str) -> str:
                    return f"You are a helpful study assistant named Study Buddy.\n\nPrevious conversation:\n{history}\n\nContext from relevant documents:\n{context}\n\nStudent: {input}\n\nStudy Buddy:"

                @kernel_function
                async def tutor(input: str, history: str, context: str) -> str:
                    return f"You are an expert tutor named Study Buddy.\nUse the Socratic method to help the student understand deeply.\n\nPrevious conversation:\n{history}\n\nContext from relevant documents:\n{context}\n\nStudent: {input}\n\nStudy Buddy (Tutor Mode):"

                @kernel_function
                async def quiz(input: str, history: str, context: str) -> str:
                    return f"You are Study Buddy in Quiz Creator mode.\nCreate 3-5 multiple-choice questions that test understanding.\n\nPrevious conversation:\n{history}\n\nContext from relevant documents:\n{context}\n\nStudent request: {input}\n\nStudy Buddy (Quiz Mode):"

                @kernel_function
                async def flashcard(input: str, history: str, context: str) -> str:
                    return f"You are Study Buddy in Flashcard Creator mode.\nCreate 5-8 flashcards covering important concepts.\n\nPrevious conversation:\n{history}\n\nContext from relevant documents:\n{context}\n\nStudent request: {input}\n\nStudy Buddy (Flashcard Mode):"

                self.study_buddy_skills = {
                    "Chat": chat,
                    "Tutor": tutor,
                    "QuizCreator": quiz,
                    "FlashcardCreator": flashcard
                }
                print(f"Created inline prompt functions: {list(self.study_buddy_skills.keys())}")
        
        return kernel
    
    async def process_message(self, user_id: str, message: str, mode: str = "chat", 
                             vector_search_client=None) -> Dict[str, Any]:
        """Process a message using the appropriate skill"""
        # Initialize conversation history if needed
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Get conversation history
        history = self.conversation_history[user_id]
        
        # Get relevant context from vector store
        context = ""
        context_sources = []
        if vector_search_client:
            search_results = await vector_search_client.search(message)
            if search_results and "results" in search_results and search_results["results"]:
                context = "\n".join([result["content"] for result in search_results["results"]])
                context_sources = [result.get("metadata", {}).get("source", "unknown") 
                                 for result in search_results["results"]]
                print(f"Found {len(search_results['results'])} relevant chunks from documents")
            else:
                print("No relevant context found in vector store")
        
        # Get the appropriate skill based on mode
        skill_name = self._get_skill_for_mode(mode)
        
        try:
            # Try to use the registered semantic skill
            if self.study_buddy_skills and skill_name in self.study_buddy_skills:
                print(f"Executing {skill_name} skill")
                
                # Create context variables
                variables = sk.ContextVariables()
                variables["input"] = message
                variables["history"] = self._format_history(history)
                variables["context"] = context
                
                # Execute the skill
                result = await self.kernel.run_async(
                    self.study_buddy_skills[skill_name],
                    input_vars=variables
                )
                
                response_text = str(result)
            # Fall back to direct GitHub model function if registered
            elif hasattr(self, 'github_completion'):
                print(f"Using GitHub model direct function for {mode} mode")
                result = await self.kernel.run_async(
                    self.github_completion,
                    input_vars=sk.ContextVariables(
                        variables={
                            "input": message,
                            "history": self._format_history(history),
                            "context": context
                        }
                    )
                )
                response_text = str(result)
            else:
                response_text = "I'm sorry, I'm having trouble accessing my skills. Please try again later."
        
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
            print(f"Error processing message: {e}")
            return {
                "response": f"I encountered an error while processing your request. Please try again. Error details: {str(e)}",
                "context_used": []
            }
    
    def _format_history(self, history):
        """Format conversation history for inclusion in prompts"""
        if not history:
            return "No previous conversation."
        
        formatted = []
        for entry in history:
            role = "Student" if entry["role"] == "user" else "Study Buddy"
            formatted.append(f"{role}: {entry['content']}")
        
        return "\n".join(formatted)
    
    def _get_skill_for_mode(self, mode):
        """Map mode to skill name"""
        mode_to_skill = {
            "chat": "Chat",
            "tutor": "Tutor",
            "quiz": "QuizCreator",
            "flashcard": "FlashcardCreator"
        }
        return mode_to_skill.get(mode, "Chat")

# Create singleton instance
study_buddy_agent = StudyBuddyAgent()