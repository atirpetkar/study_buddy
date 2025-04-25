# app/core/progress_tracker.py
from typing import Dict, Any, List
import datetime

class ProgressTracker:
    """Tracks student progress across learning activities"""
    
    def update_topic_progress(self, db, user_id: str, topic: str, 
                             activity_type: str, performance: float, 
                             confidence: float = None):
        """
        Update student progress for a topic
        
        Args:
            db: Database session
            user_id: User ID
            topic: The topic being studied
            activity_type: Type of activity (quiz, flashcard, chat)
            performance: Score between 0-1 representing performance
            confidence: Optional self-reported confidence between 0-1
        
        Returns:
            Updated progress record
        """
        from app.models import repository, models
        
        # Get existing progress
        progress = db.query(models.ProgressTracking).filter(
            models.ProgressTracking.user_id == user_id,
            models.ProgressTracking.topic == topic
        ).first()
        
        now = datetime.datetime.utcnow()
        
        if progress:
            # Update existing progress
            current_proficiency = progress.proficiency
            
            # Weight the new performance based on activity type
            weights = {
                "quiz": 0.7,
                "flashcard": 0.5,
                "chat": 0.3
            }
            activity_weight = weights.get(activity_type, 0.5)
            
            # Calculate new weighted proficiency
            updated_proficiency = (performance * activity_weight) + (current_proficiency * (1 - activity_weight))
            
            # Update confidence if provided, otherwise use a heuristic
            if confidence is not None:
                updated_confidence = (confidence * 0.6) + (progress.confidence * 0.4)
            else:
                # If proficiency improved, slightly increase confidence
                if updated_proficiency > current_proficiency:
                    updated_confidence = min(1.0, progress.confidence + 0.1)
                else:
                    updated_confidence = max(0.1, progress.confidence - 0.05)
            
            progress.proficiency = updated_proficiency
            progress.confidence = updated_confidence
            progress.last_interaction = now
            progress.interaction_type = activity_type
            
            db.commit()
            db.refresh(progress)
            return progress
        else:
            # Create new progress record
            if confidence is None:
                confidence = 0.5  # Default starting confidence
                
            new_progress = models.ProgressTracking(
                user_id=user_id,
                topic=topic,
                proficiency=performance,
                confidence=confidence,
                interaction_type=activity_type
            )
            
            db.add(new_progress)
            db.commit()
            db.refresh(new_progress)
            return new_progress
    
    def get_student_progress(self, db, user_id: str, topics: List[str] = None):
        """
        Get progress summary for a student
        
        Args:
            db: Database session
            user_id: User ID
            topics: Optional list of topics to filter by
            
        Returns:
            Dict with progress summary
        """
        from app.models import repository, models
        
        query = db.query(models.ProgressTracking).filter(
            models.ProgressTracking.user_id == user_id
        )
        
        if topics:
            query = query.filter(models.ProgressTracking.topic.in_(topics))
        
        progress_records = query.all()
        
        # Calculate average proficiency and confidence
        avg_proficiency = sum([p.proficiency for p in progress_records]) / len(progress_records) if progress_records else 0
        avg_confidence = sum([p.confidence for p in progress_records]) / len(progress_records) if progress_records else 0
        
        # Organize by topic
        topics_progress = {}
        for record in progress_records:
            topics_progress[record.topic] = {
                "proficiency": record.proficiency,
                "confidence": record.confidence,
                "last_interaction": record.last_interaction.isoformat(),
                "interaction_type": record.interaction_type
            }
        
        return {
            "user_id": user_id,
            "overall_proficiency": avg_proficiency,
            "overall_confidence": avg_confidence,
            "topics": topics_progress,
            "topics_count": len(topics_progress)
        }
    
    def generate_study_recommendations(self, db, user_id: str):
        """
        Generate personalized study recommendations based on progress
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dict with study recommendations
        """
        from app.models import repository, models
        
        # Get all progress records
        progress_records = db.query(models.ProgressTracking).filter(
            models.ProgressTracking.user_id == user_id
        ).all()
        
        # No recommendations if no progress data
        if not progress_records:
            return {
                "recommendations": [
                    "Start by taking a quiz or reviewing flashcards to build your progress profile."
                ],
                "focus_topics": []
            }
        
        # Sort topics by proficiency (ascending)
        sorted_by_proficiency = sorted(progress_records, key=lambda p: p.proficiency)
        
        # Get topics with low proficiency
        weak_topics = [p.topic for p in sorted_by_proficiency[:3] if p.proficiency < 0.7]
        
        # Get topics with high confidence but low proficiency (potential overconfidence)
        overconfident_topics = [
            p.topic for p in progress_records
            if p.confidence > 0.7 and p.proficiency < 0.6
        ]
        
        # Get topics not reviewed recently (more than 7 days)
        one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        stale_topics = [
            p.topic for p in progress_records
            if p.last_interaction < one_week_ago
        ]
        
        # Generate recommendations
        recommendations = []
        
        if weak_topics:
            weak_topics_str = ", ".join(weak_topics)
            recommendations.append(f"Focus on improving your understanding of: {weak_topics_str}")
            recommendations.append("Try using the tutoring mode to get a deeper explanation of these concepts.")
        
        if overconfident_topics:
            overconfident_topics_str = ", ".join(overconfident_topics)
            recommendations.append(f"You may need to reassess your understanding of: {overconfident_topics_str}")
            recommendations.append("Consider taking a more challenging quiz on these topics.")
        
        if stale_topics:
            stale_topics_str = ", ".join(stale_topics)
            recommendations.append(f"It's time to review these topics to reinforce your memory: {stale_topics_str}")
            recommendations.append("Review your flashcards for these topics to maintain your knowledge.")
        
        # Add a general recommendation if list is empty
        if not recommendations:
            recommendations.append("You're making good progress! Continue with regular review sessions.")
            recommendations.append("Try exploring new topics to expand your knowledge.")
        
        return {
            "recommendations": recommendations,
            "focus_topics": weak_topics + overconfident_topics,
            "review_topics": stale_topics
        }