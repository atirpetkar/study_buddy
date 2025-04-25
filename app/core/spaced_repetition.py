# app/core/spaced_repetition.py
from typing import Dict, Any, List
import datetime
import math
import json

class SpacedRepetitionScheduler:
    """
    Implements spaced repetition scheduling for flashcards based on the SuperMemo SM-2 algorithm
    with adaptations for confidence-based learning.
    """
    
    def calculate_next_review(self, confidence: int, previous_interval: int = 0, 
                             repetitions: int = 0) -> Dict[str, Any]:
        """
        Calculate the next review interval based on confidence rating
        
        Args:
            confidence: Rating from 1-5 (1 = difficult, 5 = easy)
            previous_interval: Previous interval in days (0 for first review)
            repetitions: Number of times card has been reviewed
            
        Returns:
            Dictionary with next review date and metadata
        """
        now = datetime.datetime.utcnow()
        
        # Convert confidence (1-5) to ease factor (1.3-2.5)
        # Higher confidence = higher ease factor
        ease_factor = 1.3 + (confidence - 1) * 0.3
        
        # If confidence is too low, reset repetitions
        if confidence <= 2:
            repetitions = 0
        else:
            repetitions += 1
        
        # Calculate next interval
        if repetitions == 0:
            # Failed review - show again soon (1 day)
            next_interval = 1
        elif repetitions == 1:
            # First successful review - show in 3 days
            next_interval = 3
        elif repetitions == 2:
            # Second successful review - show in 7 days
            next_interval = 7
        else:
            # Subsequent successful reviews - use SM-2 formula
            next_interval = math.ceil(previous_interval * ease_factor)
            
            # Cap at 180 days to prevent excessive intervals
            next_interval = min(next_interval, 180)
        
        # Calculate next review date
        next_review_date = now + datetime.timedelta(days=next_interval)
        
        return {
            "next_interval": next_interval,
            "next_review_date": next_review_date,
            "ease_factor": ease_factor,
            "repetitions": repetitions
        }
    
    async def update_flashcard_schedule(self, db, user_id: str, flashcard_id: str, 
                                      card_id: str, confidence: int) -> Dict[str, Any]:
        """
        Record a flashcard review and schedule the next review
        
        Args:
            db: Database session
            user_id: User ID
            flashcard_id: Flashcard set ID
            card_id: Individual card ID within the set
            confidence: Confidence rating (1-5)
            
        Returns:
            Dictionary with review data and next scheduled review
        """
        from app.models import models, repository
        
        # Get previous reviews for this card
        # We're finding reviews by flashcard_id, ideally we'd use card_id as well
        # but we'll simulate it for now
        previous_reviews = db.query(models.FlashcardReview).filter(
            models.FlashcardReview.user_id == user_id,
            models.FlashcardReview.flashcard_id == flashcard_id
        ).order_by(models.FlashcardReview.reviewed_at.desc()).all()
        
        # Calculate review parameters
        previous_interval = 0
        repetitions = 0
        
        if previous_reviews:
            # If there are previous reviews, calculate days since last review
            last_review = previous_reviews[0]
            days_since = (datetime.datetime.utcnow() - last_review.reviewed_at).days
            previous_interval = max(days_since, 1)  # At least 1 day
            
            # Count successful previous reviews (confidence 3+)
            repetitions = sum(1 for r in previous_reviews if r.confidence >= 3)
        
        # Calculate next review schedule
        schedule = self.calculate_next_review(
            confidence=confidence,
            previous_interval=previous_interval,
            repetitions=repetitions
        )
        
        # Record the review in the database
        review = repository.record_flashcard_review(
            db,
            flashcard_id=flashcard_id,
            user_id=user_id,
            confidence=confidence,
            next_review_at=schedule["next_review_date"]
        )
        
        # Update progress tracking for the topic
        # First, get the flashcard set to find the topic
        flashcard = db.query(models.Flashcard).filter(
            models.Flashcard.id == flashcard_id
        ).first()
        
        if flashcard:
            flashcard_content = json.loads(flashcard.flashcard_content) if flashcard.flashcard_content else {}
            topic = flashcard_content.get("metadata", {}).get("topic", "General")
            
            # Update progress - confidence from 1-5 to 0-1 scale
            confidence_normalized = (confidence - 1) / 4.0
            repository.update_topic_progress(
                db,
                user_id=user_id,
                topic=topic,
                activity_type="flashcard",
                performance=confidence_normalized,
                confidence=confidence_normalized
            )
        
        return {
            "review_id": review.id,
            "flashcard_id": flashcard_id,
            "card_id": card_id,
            "reviewed_at": review.reviewed_at.isoformat(),
            "confidence": confidence,
            "next_review_at": schedule["next_review_date"].isoformat(),
            "interval_days": schedule["next_interval"]
        }
    
    async def get_due_flashcards(self, db, user_id: str) -> List[Dict[str, Any]]:
        """
        Get flashcards that are due for review
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of flashcards due for review
        """
        from app.models import models
        import json
        
        now = datetime.datetime.utcnow()
        
        # Get the latest review for each flashcard
        flashcard_ids = []
        flashcard_id_to_review = {}
        
        # This query gets the latest review for each flashcard
        reviews = db.query(models.FlashcardReview).filter(
            models.FlashcardReview.user_id == user_id
        ).order_by(models.FlashcardReview.reviewed_at.desc()).all()
        
        # Group by flashcard_id and keep only the latest
        for review in reviews:
            if review.flashcard_id not in flashcard_id_to_review:
                flashcard_id_to_review[review.flashcard_id] = review
        
        # Check which flashcards are due
        due_flashcard_ids = []
        for flashcard_id, review in flashcard_id_to_review.items():
            if review.next_review_at and review.next_review_at <= now:
                due_flashcard_ids.append(flashcard_id)
        
        # Fetch the flashcard details
        due_flashcards = []
        if due_flashcard_ids:
            flashcards = db.query(models.Flashcard).filter(
                models.Flashcard.id.in_(due_flashcard_ids)
            ).all()
            
            for flashcard in flashcards:
                content = json.loads(flashcard.flashcard_content) if flashcard.flashcard_content else {}
                
                # Add to result with review information
                review = flashcard_id_to_review[flashcard.id]
                due_flashcards.append({
                    "id": flashcard.id,
                    "content": content,
                    "last_review": review.reviewed_at.isoformat(),
                    "due_date": review.next_review_at.isoformat(),
                    "last_confidence": review.confidence
                })
        
        return due_flashcards