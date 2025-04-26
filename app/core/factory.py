# app/core/factory.py
import os
from typing import Dict, Any, Optional

# Import existing implementations
from app.core.message_processor import MessageProcessor
from app.core.quiz_generator import QuizGenerator
from app.core.flashcard_generator import FlashcardGenerator
from app.core.tutoring import TutoringSessionManager
from app.core.personalization_engine import PersonalizationEngine
from app.core.study_planner import StudyPlanGenerator

# Import SK implementations (will be created)
try:
    from app.core.sk.connectors.processor_adapter import SKMessageProcessor
    from app.core.sk.skills.quiz_skill import SKQuizGenerator
    from app.core.sk.skills.flashcard_skill import SKFlashcardGenerator
    from app.core.sk.skills.tutor_skill import SKTutoringManager
    from app.core.sk.skills.personalization_skill import SKPersonalizationEngine
    from app.core.sk.planners.study_planner import SKStudyPlanGenerator
    SK_AVAILABLE = True
except ImportError:
    SK_AVAILABLE = False

class StudyBuddyFactory:
    """Factory for creating Study Buddy components with optional SK integration"""
    
    def __init__(self):
        """Initialize the factory"""
        # Check for environment toggle
        self.use_sk = os.getenv("USE_SK", "false").lower() == "true"
        # Fall back to direct implementation if SK is not available
        if self.use_sk and not SK_AVAILABLE:
            self.use_sk = False
            print("Warning: Semantic Kernel not available, falling back to direct implementation")
    
    def get_message_processor(self) -> MessageProcessor:
        """Get the appropriate message processor implementation"""
        if self.use_sk and SK_AVAILABLE:
            return SKMessageProcessor()
        return MessageProcessor()
    
    def get_quiz_generator(self) -> QuizGenerator:
        """Get the appropriate quiz generator implementation"""
        if self.use_sk and SK_AVAILABLE:
            return SKQuizGenerator()
        return QuizGenerator()
    
    def get_flashcard_generator(self) -> FlashcardGenerator:
        """Get the appropriate flashcard generator implementation"""
        if self.use_sk and SK_AVAILABLE:
            return SKFlashcardGenerator()
        return FlashcardGenerator()
    
    def get_tutoring_manager(self) -> TutoringSessionManager:
        """Get the appropriate tutoring manager implementation"""
        if self.use_sk and SK_AVAILABLE:
            return SKTutoringManager()
        return TutoringSessionManager()
    
    def get_personalization_engine(self) -> PersonalizationEngine:
        """Get the appropriate personalization engine implementation"""
        if self.use_sk and SK_AVAILABLE:
            return SKPersonalizationEngine()
        return PersonalizationEngine()
    
    def get_study_planner(self) -> StudyPlanGenerator:
        """Get the appropriate study planner implementation"""
        if self.use_sk and SK_AVAILABLE:
            return SKStudyPlanGenerator()
        return StudyPlanGenerator()

# Create singleton instance
_factory = StudyBuddyFactory()

def get_factory() -> StudyBuddyFactory:
    """Get the singleton factory instance"""
    return _factory