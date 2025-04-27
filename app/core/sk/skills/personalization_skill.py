# app/core/sk/skills/personalization_skill.py
from typing import Dict, Any, List, Optional
import json
import semantic_kernel as sk
from semantic_kernel.functions import kernel_function
from app.core.personalization_engine import PersonalizationEngine

class PersonalizationSkill:
    """Semantic Kernel implementation of personalization functionality"""
    
    def __init__(self, kernel):
        """Initialize the personalization skill"""
        self.kernel = kernel
        self.personalization_engine = PersonalizationEngine()
    
    @kernel_function(
        description="Analyze user's learning style based on conversation history",
        name="AnalyzeLearningStyle"
    )
    async def analyze_learning_style(self, user_id: str, history: str) -> str:
        """Analyze user's learning style using SK function format"""
        # In a real implementation, this would use SK's LLM capabilities
        # For now, just pass through to the regular PersonalizationEngine
        
        # Parse history from string to list
        try:
            conversation_history = json.loads(history) if history else []
        except:
            conversation_history = []
        
        # Get the database session
        from app.models.db import get_db
        db = next(get_db())
        
        # Call the standard personalization engine
        result = await self.personalization_engine.analyze_learning_style(
            db=db, 
            user_id=user_id, 
            conversation_history=conversation_history
        )
        
        # Convert to string format for SK
        return json.dumps(result)

class SKPersonalizationEngine(PersonalizationEngine):
    """SK adapter for PersonalizationEngine that maintains the same interface"""
    
    def __init__(self):
        """Initialize the SK personalization engine"""
        super().__init__()
        # Defer the kernel import until it's actually needed
        self.kernel = None
    
    def _ensure_kernel(self):
        """Lazy-load the kernel only when needed"""
        if self.kernel is None:
            # Import here to avoid circular dependency
            from app.core.sk.kernel_factory import get_kernel
            self.kernel = get_kernel()
    
    async def analyze_learning_style(self, db, user_id: str, conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        TODO: Implement a proper SK version of analyze_learning_style
        For now, just use the base implementation
        """
        # Ensure kernel is loaded
        self._ensure_kernel()
        
        # For now, just use the parent class implementation
        return await super().analyze_learning_style(db, user_id, conversation_history)
    
    async def adapt_content_for_style(self, content: Dict[str, Any], learning_style: Dict[str, Any]) -> Dict[str, Any]:
        """
        TODO: Implement a proper SK version of adapt_content_for_style
        For now, just use the base implementation
        """
        # Ensure kernel is loaded
        self._ensure_kernel()
        
        # For now, just use the parent class implementation
        return await super().adapt_content_for_style(content, learning_style)
    
    async def generate_personalized_quiz(self, db, user_id: str, topic: str, 
                                      quiz_generator=None, vector_client=None, 
                                      processor=None) -> Dict[str, Any]:
        """
        TODO: Implement a proper SK version of generate_personalized_quiz
        For now, just use the base implementation
        """
        # Ensure kernel is loaded
        self._ensure_kernel()
        
        # For now, just use the parent class implementation
        return await super().generate_personalized_quiz(
            db, user_id, topic, quiz_generator, vector_client, processor
        )

def register_personalization_skill(kernel: sk.Kernel):
    """Register the personalization skill with the kernel"""
    skill = PersonalizationSkill(kernel)
    kernel.add_skill(skill, skill_name="PersonalizationSkill")