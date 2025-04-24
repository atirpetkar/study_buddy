import os
from typing import List, Dict, Any
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()

class StudyBuddyAgent:
    def __init__(self):
        self.conversation_history = {}  # Simple in-memory storage for now
        self._setup_client()
        
    def _setup_client(self):
        """Set up OpenAI client for GitHub's models"""
        token = os.environ.get("GITHUB_TOKEN")
        endpoint = os.getenv("ENDPOINT")
        self.model_name = os.getenv("GITHUB_MODEL", "openai/gpt-4o")
        
        self.client = AsyncOpenAI(
            base_url=endpoint,
            api_key=token,
        )
        
        print(f"OpenAI client configured for model: {self.model_name}")
    
    def _load_prompt_template(self, mode_name):
        """Load prompt template from file"""
        skills_directory = os.path.join(os.path.dirname(__file__), "..", "skills")
        prompt_path = os.path.join(skills_directory, "StudyBuddy", mode_name, "skprompt.txt")
        try:
            with open(prompt_path, "r") as f:
                return f.read()
        except Exception as e:
            print(f"Error loading {mode_name} prompt file: {e}")
            # Return fallback prompts if file not found
            if mode_name == "Chat":
                return "You are a helpful study assistant named Study Buddy.\n\nPrevious conversation:\n{{$history}}\n\nContext from relevant documents:\n{{$context}}\n\nStudent: {{$input}}\n\nStudy Buddy:"
            elif mode_name == "Tutor":
                return "You are an expert tutor named Study Buddy.\nUse the Socratic method to help the student understand deeply.\n\nPrevious conversation:\n{{$history}}\n\nContext from relevant documents:\n{{$context}}\n\nStudent: {{$input}}\n\nStudy Buddy (Tutor Mode):"
            elif mode_name == "QuizCreator":
                return "You are Study Buddy in Quiz Creator mode.\nCreate 3-5 multiple-choice questions that test understanding.\n\nPrevious conversation:\n{{$history}}\n\nContext from relevant documents:\n{{$context}}\n\nStudent request: {{$input}}\n\nStudy Buddy (Quiz Mode):"
            elif mode_name == "FlashcardCreator":
                return "You are Study Buddy in Flashcard Creator mode.\nCreate 5-8 flashcards covering important concepts.\n\nPrevious conversation:\n{{$history}}\n\nContext from relevant documents:\n{{$context}}\n\nStudent request: {{$input}}\n\nStudy Buddy (Flashcard Mode):"
    
    def _load_config(self, mode_name):
        """Load config from file"""
        skills_directory = os.path.join(os.path.dirname(__file__), "..", "skills")
        config_path = os.path.join(skills_directory, "StudyBuddy", mode_name, "config.json")
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                return config.get("completion", {})
        except Exception as e:
            print(f"Error loading {mode_name} config file: {e}")
            # Default configs
            return {
                "max_tokens": 1000,
                "temperature": 0.7
            }
    
    async def process_message(self, user_id: str, message: str, mode: str = "chat", 
                             vector_search_client=None) -> Dict[str, Any]:
        """Process a message using GitHub's models via OpenAI client"""
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
        
        # Get the appropriate mode
        skill_name = self._get_skill_for_mode(mode)
        
        try:
            # Load the prompt template and config
            prompt_template = self._load_prompt_template(skill_name)
            config = self._load_config(skill_name)
            
            # Format the prompt
            formatted_history = self._format_history(history)
            prompt = prompt_template.replace("{{$input}}", message)
            prompt = prompt.replace("{{$history}}", formatted_history)
            prompt = prompt.replace("{{$context}}", context)
            
            print(f"Sending prompt to model with {skill_name} mode")
            
            # Prepare messages for the API using GitHub's method
            messages = [
                {"role": "system", "content": "You are Study Buddy, an AI tutor."},
                {"role": "user", "content": prompt}
            ]
            
            # Call the OpenAI client with GitHub's model
            response = await self.client.chat.completions.create(
                messages=messages,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 1000),
                model=self.model_name
            )
            
            # Extract response text
            response_text = response.choices[0].message.content
            
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
            import traceback
            traceback.print_exc()
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