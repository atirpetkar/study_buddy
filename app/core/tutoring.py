# app/core/tutoring.py
from typing import List, Set, Dict, Any
import re

class TutoringSession:
    def __init__(self):
        self.current_topic = None
        self.concepts_covered = set()
        self.questions_asked = []
        self.confidence_level = "medium"  # low, medium, high
        self.session_stage = "identify"  # identify, question, guide, validate, connect
    
    def update_stage(self, new_stage: str) -> None:
        """Update the current stage of the tutoring session"""
        self.session_stage = new_stage
    
    def add_concept(self, concept: str) -> None:
        """Track a covered concept"""
        self.concepts_covered.add(concept)
    
    def record_question(self, question: str) -> None:
        """Record a question asked by the tutor"""
        self.questions_asked.append(question)
    
    def set_confidence(self, level: str) -> None:
        """Update student's confidence level"""
        self.confidence_level = level
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get a dictionary with the current session information"""
        return {
            "topic": self.current_topic,
            "concepts": list(self.concepts_covered),
            "questions_count": len(self.questions_asked),
            "confidence": self.confidence_level,
            "stage": self.session_stage
        }
    
    def format_session_context(self) -> str:
        """Format session info for inclusion in prompts"""
        info = self.get_session_info()
        return f"""
Current tutoring session info:
- Topic: {info['topic'] or 'Not set'}
- Concepts covered: {', '.join(info['concepts']) if info['concepts'] else 'None yet'}
- Questions asked: {info['questions_count']}
- Student confidence level: {info['confidence']}
- Current stage: {info['stage']}
"""

    def analyze_response(self, response_text: str) -> None:
        """Analyze tutor response to update session state"""
        # Extract questions asked
        questions = re.findall(r'.*\?', response_text)
        for question in questions:
            self.record_question(question.strip())
        
        # Heuristic to determine stage - simplified version
        if "understand" in response_text.lower() or "know" in response_text.lower():
            self.update_stage("identify")
        elif "?" in response_text:
            self.update_stage("question")
        elif "hint" in response_text.lower():
            self.update_stage("guide")
        elif "correct" in response_text.lower() or "exactly" in response_text.lower():
            self.update_stage("validate")
        elif "related" in response_text.lower() or "also" in response_text.lower():
            self.update_stage("connect")

class TutoringSessionManager:
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, user_id: str) -> TutoringSession:
        """Get or create a tutoring session for a user"""
        session_key = f"{user_id}_tutor"
        if session_key not in self.sessions:
            self.sessions[session_key] = TutoringSession()
        return self.sessions[session_key]