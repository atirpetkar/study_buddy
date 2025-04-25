# app/core/quiz_attempt.py
from typing import List, Dict, Any
import uuid

class QuizScorer:
    """Handles scoring of quiz attempts"""
    
    def score_attempt(self, quiz: Dict[str, Any], user_answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Score a quiz attempt
        
        Args:
            quiz: The complete quiz with questions and correct answers
            user_answers: Dictionary mapping question IDs to user's answer choices
            
        Returns:
            Dict with score details and feedback
        """
        if not quiz or "questions" not in quiz:
            return {"error": "Invalid quiz format"}
        
        questions = quiz["questions"]
        total_questions = len(questions)
        correct_count = 0
        question_results = []
        
        for question in questions:
            q_id = question["id"]
            is_correct = False
            user_answer = user_answers.get(q_id, None)
            
            if user_answer and user_answer == question["correct_answer"]:
                correct_count += 1
                is_correct = True
            
            # Add result for this question
            question_results.append({
                "question_id": q_id,
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": question["correct_answer"],
                "explanation": question["explanation"]
            })
        
        # Calculate score percentage
        score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        return {
            "attempt_id": str(uuid.uuid4()),
            "score": {
                "correct": correct_count,
                "total": total_questions,
                "percentage": score_percentage
            },
            "question_results": question_results,
            "feedback": self._generate_feedback(score_percentage, question_results)
        }
    
    def _generate_feedback(self, score_percentage: float, question_results: List[Dict[str, Any]]) -> str:
        """Generate feedback based on quiz performance"""
        if score_percentage >= 90:
            feedback = "Excellent work! You have a strong understanding of this material."
        elif score_percentage >= 70:
            feedback = "Good job! You understand most of the concepts, but there's room for improvement."
        elif score_percentage >= 50:
            feedback = "You're making progress. Review the concepts you missed and try again."
        else:
            feedback = "You might need more study time with this material. Focus on the explanations provided."
        
        # Add specific feedback on missed questions
        missed_questions = [result for result in question_results if not result["correct"]]
        if missed_questions:
            feedback += "\n\nFocus on reviewing these concepts:\n"
            for idx, result in enumerate(missed_questions[:3]):  # Limit to first 3 missed questions
                explanation = result["explanation"]
                feedback += f"• {explanation}\n"
            
            if len(missed_questions) > 3:
                feedback += f"• Plus {len(missed_questions) - 3} more concepts to review."
        
        return feedback