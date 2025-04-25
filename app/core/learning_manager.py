# app/core/learning_manager.py
from typing import Dict, Any, List
import datetime
import json

class LearningManager:
    """Manages learning progress across all activities"""
    
    async def generate_dashboard(self, db, user_id: str) -> Dict[str, Any]:
        """Generate a comprehensive learning dashboard for a student"""
        from app.models import models
        
        # Get progress records
        progress_records = db.query(models.ProgressTracking).filter(
            models.ProgressTracking.user_id == user_id
        ).all()
        
        # Empty dashboard if no records
        if not progress_records:
            return {
                "user_id": user_id,
                "overall_proficiency": 0.0,
                "overall_confidence": 0.0,
                "topics": [],
                "recent_activities": [],
                "activity_summary": {
                    "total_quizzes": 0,
                    "avg_quiz_score": 0.0,
                    "total_flashcards_reviewed": 0,
                    "avg_flashcard_confidence": 0.0,
                    "tutoring_sessions": 0,
                },
                "recommendations": [
                    "Start your learning journey by taking a quiz or reviewing flashcards.",
                    "Upload study materials to get personalized learning content."
                ]
            }
        
        # Calculate overall metrics
        overall_proficiency = sum(p.proficiency for p in progress_records) / len(progress_records)
        overall_confidence = sum(p.confidence for p in progress_records) / len(progress_records)
        
        # Get recent activities (last 7 days)
        seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        
        # Gather quiz attempts
        quiz_attempts = db.query(models.QuizAttempt).filter(
            models.QuizAttempt.user_id == user_id,
            models.QuizAttempt.taken_at >= seven_days_ago
        ).order_by(models.QuizAttempt.taken_at.desc()).all()
        
        # Gather flashcard reviews
        flashcard_reviews = db.query(models.FlashcardReview).filter(
            models.FlashcardReview.user_id == user_id,
            models.FlashcardReview.reviewed_at >= seven_days_ago
        ).order_by(models.FlashcardReview.reviewed_at.desc()).all()
        
        # Format activities for display
        recent_activities = []
        
        # Add quiz activities
        for qa in quiz_attempts[:5]:
            quiz = db.query(models.Quiz).filter(models.Quiz.id == qa.quiz_id).first()
            quiz_content = json.loads(quiz.quiz_content) if quiz and quiz.quiz_content else {}
            
            recent_activities.append({
                "type": "quiz",
                "date": qa.taken_at.isoformat(),
                "score": qa.score,
                "topic": quiz_content.get("metadata", {}).get("topic", "Unknown topic")
            })
        
        # Add flashcard activities
        for fr in flashcard_reviews[:5]:
            flashcard = db.query(models.Flashcard).filter(models.Flashcard.id == fr.flashcard_id).first()
            flashcard_content = json.loads(flashcard.flashcard_content) if flashcard and flashcard.flashcard_content else {}
            
            recent_activities.append({
                "type": "flashcard",
                "date": fr.reviewed_at.isoformat(),
                "confidence": fr.confidence,
                "topic": flashcard_content.get("metadata", {}).get("topic", "Unknown topic")
            })
        
        # Sort activities by date
        recent_activities.sort(key=lambda x: x["date"], reverse=True)
        
        # Process topic-specific progress data
        topics_progress = []
        topic_set = set(p.topic for p in progress_records)
        
        for topic in topic_set:
            topic_records = [p for p in progress_records if p.topic == topic]
            if not topic_records:
                continue
                
            # Get latest record for this topic
            latest_record = max(topic_records, key=lambda p: p.last_interaction)
            
            # Determine strengths and weaknesses
            strengths = []
            weaknesses = []
            
            if latest_record.proficiency > 0.7:
                strengths.append("High proficiency")
            elif latest_record.proficiency < 0.4:
                weaknesses.append("Low proficiency")
                
            if latest_record.confidence > 0.7 and latest_record.proficiency > 0.6:
                strengths.append("Confident understanding")
            elif latest_record.confidence > 0.7 and latest_record.proficiency < 0.5:
                weaknesses.append("Overconfidence")
            
            # Add to topics progress
            topics_progress.append({
                "topic": topic,
                "proficiency": latest_record.proficiency,
                "confidence": latest_record.confidence,
                "last_activity_date": latest_record.last_interaction.isoformat(),
                "strengths": strengths,
                "weaknesses": weaknesses
            })
        
        # Generate activity summary
        total_quizzes = len(quiz_attempts)
        avg_quiz_score = sum(qa.score for qa in quiz_attempts) / total_quizzes if total_quizzes > 0 else 0
        
        total_flashcards = len(flashcard_reviews)
        avg_flashcard_confidence = sum(fr.confidence for fr in flashcard_reviews) / total_flashcards if total_flashcards > 0 else 0
        
        # Generate recommendations
        recommendations = await self.generate_recommendations(db, user_id)
        
        return {
            "user_id": user_id,
            "overall_proficiency": overall_proficiency,
            "overall_confidence": overall_confidence,
            "topics": topics_progress,
            "recent_activities": recent_activities,
            "activity_summary": {
                "total_quizzes": total_quizzes,
                "avg_quiz_score": avg_quiz_score,
                "total_flashcards_reviewed": total_flashcards,
                "avg_flashcard_confidence": avg_flashcard_confidence,
                "tutoring_sessions": 0
            },
            "recommendations": recommendations.get("recommendations", [])
        }
    
    async def get_topic_progress(self, db, user_id: str, topic: str) -> Dict[str, Any]:
        """Get detailed progress for a specific topic"""
        from app.models import models
        
        # Get progress records for this topic
        progress = db.query(models.ProgressTracking).filter(
            models.ProgressTracking.user_id == user_id,
            models.ProgressTracking.topic == topic
        ).order_by(models.ProgressTracking.last_interaction.desc()).all()
        
        if not progress:
            return {
                "user_id": user_id,
                "topic": topic,
                "proficiency": 0.0,
                "confidence": 0.0,
                "activities": [],
                "concepts_mastered": [],
                "concepts_struggling": []
            }
        
        # Get latest progress record
        latest_progress = progress[0]
        
        # Get quiz attempts related to this topic
        quiz_attempts = []
        quizzes = db.query(models.Quiz).filter(models.Quiz.user_id == user_id).all()
        
        for quiz in quizzes:
            content = json.loads(quiz.quiz_content) if quiz.quiz_content else {}
            quiz_topic = content.get("metadata", {}).get("topic")
            
            if quiz_topic == topic:
                # Get attempts for this quiz
                attempts = db.query(models.QuizAttempt).filter(
                    models.QuizAttempt.quiz_id == quiz.id,
                    models.QuizAttempt.user_id == user_id
                ).order_by(models.QuizAttempt.taken_at.desc()).all()
                
                for attempt in attempts:
                    quiz_attempts.append({
                        "quiz_id": quiz.id,
                        "taken_at": attempt.taken_at.isoformat(),
                        "score": attempt.score
                    })
        
        # Get flashcard reviews related to this topic
        flashcard_reviews = []
        flashcards = db.query(models.Flashcard).filter(models.Flashcard.user_id == user_id).all()
        
        for flashcard in flashcards:
            content = json.loads(flashcard.flashcard_content) if flashcard.flashcard_content else {}
            flashcard_topic = content.get("metadata", {}).get("topic")
            
            if flashcard_topic == topic:
                # Get reviews for this flashcard
                reviews = db.query(models.FlashcardReview).filter(
                    models.FlashcardReview.flashcard_id == flashcard.id,
                    models.FlashcardReview.user_id == user_id
                ).order_by(models.FlashcardReview.reviewed_at.desc()).all()
                
                for review in reviews:
                    flashcard_reviews.append({
                        "flashcard_id": flashcard.id,
                        "reviewed_at": review.reviewed_at.isoformat(),
                        "confidence": review.confidence
                    })
        
        # Merge activities in chronological order
        activities = []
        
        for attempt in quiz_attempts:
            activities.append({
                "type": "quiz",
                "date": attempt["taken_at"],
                "score": attempt["score"]
            })
        
        for review in flashcard_reviews:
            activities.append({
                "type": "flashcard",
                "date": review["reviewed_at"],
                "confidence": review["confidence"]
            })
        
        # Sort activities by date
        activities.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "user_id": user_id,
            "topic": topic,
            "proficiency": latest_progress.proficiency,
            "confidence": latest_progress.confidence,
            "activities": activities[:10],  # Limit to 10 most recent
            "concepts_mastered": [],  # Simplified version
            "concepts_struggling": []  # Simplified version
        }
    
    async def record_activity(self, db, user_id: str, activity_type: str, 
                            topic: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Record a learning activity and update progress"""
        from app.models import repository
        
        # Calculate performance score based on activity type
        performance = 0.0
        confidence = None
        
        if activity_type == "quiz":
            performance = details.get("score", 0) / 100  # Convert percentage to 0-1
        elif activity_type == "flashcard":
            confidence = details.get("confidence", 3) / 5  # Convert 1-5 to 0-1
            performance = confidence
        elif activity_type == "tutoring":
            performance = details.get("understanding", 0.5)  # 0-1 scale
        
        # Update progress tracking
        updated_progress = repository.update_topic_progress(
            db,
            user_id=user_id,
            topic=topic,
            activity_type=activity_type,
            performance=performance,
            confidence=confidence
        )
        
        return {
            "user_id": user_id,
            "topic": topic,
            "activity_type": activity_type,
            "updated_proficiency": updated_progress.proficiency,
            "updated_confidence": updated_progress.confidence
        }
    
    async def generate_recommendations(self, db, user_id: str) -> Dict[str, Any]:
        """Generate personalized study recommendations based on progress data"""
        from app.models import models
        
        # Get all progress records for this user
        progress_records = db.query(models.ProgressTracking).filter(
            models.ProgressTracking.user_id == user_id
        ).all()
        
        if not progress_records:
            return {
                "user_id": user_id,
                "recommendations": [
                    "Start your learning journey by taking a quiz or reviewing flashcards.",
                    "Upload study materials to get personalized learning content."
                ]
            }
        
        # Find topics needing attention
        now = datetime.datetime.utcnow()
        two_weeks_ago = now - datetime.timedelta(days=14)
        
        # Prioritize different types of topics
        weak_topics = [p.topic for p in progress_records if p.proficiency < 0.5]
        overconfident_topics = [p.topic for p in progress_records if p.confidence > 0.7 and p.proficiency < 0.5]
        stale_topics = [p.topic for p in progress_records if p.last_interaction < two_weeks_ago]
        
        # Generate recommendations
        recommendations = []
        
        if overconfident_topics:
            topic = overconfident_topics[0]
            recommendations.append(f"Your confidence in '{topic}' may be higher than your actual proficiency. Take a challenging quiz to identify knowledge gaps.")
        
        if weak_topics:
            topic = weak_topics[0]
            recommendations.append(f"You're struggling with '{topic}'. Consider a tutoring session to build a stronger foundation.")
        
        if stale_topics:
            topic = stale_topics[0]
            recommendations.append(f"It's been over two weeks since you studied '{topic}'. Review flashcards to maintain your knowledge.")
        
        # Add general recommendations if needed
        if not recommendations:
            recommendations.append("You're making good progress! Continue with regular review sessions.")
            recommendations.append("Try exploring new topics to expand your knowledge.")
        
        return {
            "user_id": user_id,
            "recommendations": recommendations
        }
    
    async def get_spaced_repetition_schedule(self, db, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Generate a spaced repetition schedule for upcoming days"""
        from app.models import models
        
        now = datetime.datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get all flashcard reviews with future review dates
        reviews = db.query(models.FlashcardReview).filter(
            models.FlashcardReview.user_id == user_id
        ).order_by(models.FlashcardReview.next_review_at).all()
        
        # Organize reviews by date
        overdue = []
        today_items = []
        upcoming = {}
        
        for review in reviews:
            if not review.next_review_at:
                continue
                
            flashcard = db.query(models.Flashcard).filter(
                models.Flashcard.id == review.flashcard_id
            ).first()
            
            if not flashcard:
                continue
                
            content = json.loads(flashcard.flashcard_content) if flashcard.flashcard_content else {}
            topic = content.get("metadata", {}).get("topic", "Unknown")
            
            # Create review item
            review_item = {
                "id": review.id,
                "type": "flashcard",
                "topic": topic,
                "due_date": review.next_review_at.isoformat()
            }
            
            # Categorize by date
            review_date = review.next_review_at.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if review_date < today:
                overdue.append(review_item)
            elif review_date == today:
                today_items.append(review_item)
            else:
                # Only include upcoming days within the specified range
                days_ahead = (review_date - today).days
                if days_ahead <= days:
                    date_str = review_date.strftime("%Y-%m-%d")
                    if date_str not in upcoming:
                        upcoming[date_str] = []
                    upcoming[date_str].append(review_item)
        
        return {
            "user_id": user_id,
            "today": today_items,
            "overdue": overdue,
            "upcoming": upcoming
        }
        
    async def get_all_progress(self, db, user_id: str) -> Dict[str, Any]:
        """Get all progress data for a user in a structured format"""
        from app.models import models
        
        # Get all progress records
        progress_records = db.query(models.ProgressTracking).filter(
            models.ProgressTracking.user_id == user_id
        ).all()
        
        topics_data = {}
        for record in progress_records:
            topic = record.topic
            if topic not in topics_data:
                topics_data[topic] = {
                    "proficiency": record.proficiency,
                    "confidence": record.confidence,
                    "last_interaction": record.last_interaction.isoformat(),
                    "interaction_type": record.interaction_type
                }
        
        return {
            "user_id": user_id,
            "topics": topics_data
        }