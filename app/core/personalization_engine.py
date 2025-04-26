# app/core/personalization_engine.py
from typing import Dict, Any, List, Optional
import datetime
import json
import re

class PersonalizationEngine:
    """
    Engine for personalized learning experiences based on user profile, 
    progress, and detected learning style.
    """
    
    # Learning style categories
    LEARNING_STYLES = {
        "visual": {
            "keywords": ["see", "view", "look", "watch", "observe", "visual", "picture", "image", "diagram", "chart"],
            "patterns": ["I see what you mean", "I need to see it", "show me", "looks good", "I can picture that"]
        },
        "auditory": {
            "keywords": ["hear", "listen", "sound", "talk", "discuss", "audio", "noise", "loud", "quiet"],
            "patterns": ["I hear what you're saying", "sounds good", "let's talk about", "I'm listening", "tell me"]
        },
        "reading_writing": {
            "keywords": ["read", "write", "note", "text", "list", "document", "book", "article", "word"],
            "patterns": ["let me write that down", "I've read that", "in my notes", "make a list", "write it out"]
        },
        "kinesthetic": {
            "keywords": ["do", "feel", "touch", "practice", "try", "experience", "hands-on", "motion", "action"],
            "patterns": ["let me try", "I feel like", "hands-on", "let's practice", "I need to experience it"]
        }
    }
    
    def __init__(self):
        self.default_style = "reading_writing"  # Default style if no clear preference detected
    
    async def analyze_learning_style(self, db, user_id: str, conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Detect learning style based on conversation history and user behavior.
        
        Args:
            db: Database session
            user_id: User ID
            conversation_history: Optional list of conversation entries
            
        Returns:
            Dict with detected learning style and confidence scores
        """
        from app.models import models, repository
        
        # Get user profile
        profile = repository.get_user_profile(db, user_id)
        profile_data = {}
        
        if profile:
            # Use existing learning style information if available
            profile_data = profile.get("study_preferences", {})
            if profile_data and "learning_style" in profile_data:
                existing_style = profile_data.get("learning_style", {})
                if existing_style and existing_style.get("last_updated"):
                    # Only use if recently updated (last 30 days)
                    last_updated = datetime.datetime.fromisoformat(existing_style["last_updated"])
                    if (datetime.datetime.utcnow() - last_updated).days < 30:
                        return existing_style
        
        # Get conversations if not provided
        if not conversation_history:
            conversations = db.query(models.Conversation).filter(
                models.Conversation.user_id == user_id
            ).order_by(models.Conversation.created_at.desc()).limit(20).all()
            
            conversation_history = [
                {"role": "user", "content": conv.message} 
                for conv in conversations
            ]
        
        # Analyze learning style based on conversation patterns
        style_scores = self._analyze_text_for_style(conversation_history)
        
        # Analyze activity patterns
        activity_styles = self._analyze_activity_patterns(db, user_id)
        
        # Combine both analyses with appropriate weights
        final_scores = {}
        # 60% weight to conversation analysis, 40% to activity analysis
        for style, score in style_scores.items():
            final_scores[style] = score * 0.6
            
        for style, score in activity_styles.items():
            if style in final_scores:
                final_scores[style] += score * 0.4
            else:
                final_scores[style] = score * 0.4
        
        # Normalize scores
        total = sum(final_scores.values()) if sum(final_scores.values()) > 0 else 1
        normalized_scores = {style: score/total for style, score in final_scores.items()}
        
        # Get primary and secondary styles
        sorted_styles = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        primary_style = sorted_styles[0][0] if sorted_styles else self.default_style
        secondary_style = sorted_styles[1][0] if len(sorted_styles) > 1 else None
        
        # Clear confidence - how strong is the primary vs others
        if len(sorted_styles) > 1:
            primary_confidence = sorted_styles[0][1] - sorted_styles[1][1]
        else:
            primary_confidence = 1.0
            
        result = {
            "primary_style": primary_style,
            "secondary_style": secondary_style,
            "confidence": primary_confidence,
            "scores": normalized_scores,
            "last_updated": datetime.datetime.utcnow().isoformat()
        }
        
        # Update user profile with learning style
        if profile:
            preferences = profile_data or {}
            preferences["learning_style"] = result
            repository.update_user_profile(db, user_id, {"study_preferences": preferences})
        
        return result
    
    def _analyze_text_for_style(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Analyze conversation text for learning style indicators
        
        Args:
            conversation_history: List of conversation entries
            
        Returns:
            Dict with scores for each learning style
        """
        style_scores = {style: 0 for style in self.LEARNING_STYLES.keys()}
        
        if not conversation_history:
            return style_scores
            
        # Combine all user messages
        all_text = " ".join([
            entry["content"].lower() 
            for entry in conversation_history 
            if entry.get("role") == "user" and entry.get("content")
        ])
        
        # Count keyword occurrences
        for style, indicators in self.LEARNING_STYLES.items():
            # Check keywords
            for keyword in indicators["keywords"]:
                # Count word occurrences with word boundaries
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, all_text)
                style_scores[style] += len(matches)
            
            # Check patterns (phrases)
            for pattern in indicators["patterns"]:
                if pattern.lower() in all_text:
                    # Patterns get higher weight than single keywords
                    style_scores[style] += 2
        
        return style_scores
    
    def _analyze_activity_patterns(self, db, user_id: str) -> Dict[str, float]:
        """
        Analyze user activity patterns for learning style indicators
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dict with scores for each learning style
        """
        from app.models import models
        
        style_scores = {style: 0 for style in self.LEARNING_STYLES.keys()}
        
        try:
            # Analyze quiz attempts (favors reading/writing)
            quiz_attempts = db.query(models.QuizAttempt).filter(
                models.QuizAttempt.user_id == user_id
            ).all()
            style_scores["reading_writing"] += len(quiz_attempts) * 0.5
            
            # Analyze flashcard reviews (favors visual and reading/writing)
            flashcard_reviews = db.query(models.FlashcardReview).filter(
                models.FlashcardReview.user_id == user_id
            ).all()
            style_scores["visual"] += len(flashcard_reviews) * 0.3
            style_scores["reading_writing"] += len(flashcard_reviews) * 0.2
            
            # Analyze conversation history (favors auditory)
            conversations = db.query(models.Conversation).filter(
                models.Conversation.user_id == user_id
            ).all()
            style_scores["auditory"] += len(conversations) * 0.4
            
            # Look for patterns in time spent on different activities
            # (Would need more data to implement fully)
        
        except Exception as e:
            print(f"Error analyzing activity patterns: {e}")
        
        return style_scores
    
    async def adapt_content_for_style(self, content: Dict[str, Any], learning_style: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt learning content based on detected learning style
        
        Args:
            content: Original content to adapt
            learning_style: Learning style information
            
        Returns:
            Adapted content with style-specific enhancements
        """
        primary_style = learning_style.get("primary_style", self.default_style)
        adapted_content = dict(content)  # Make a copy
        
        # Add style-specific enhancements
        if primary_style == "visual":
            adapted_content["presentation_hints"] = [
                "Include diagrams where possible",
                "Use visual metaphors to explain concepts",
                "Incorporate charts and graphs for data",
                "Use color coding for important information"
            ]
        elif primary_style == "auditory":
            adapted_content["presentation_hints"] = [
                "Suggest reading explanations aloud",
                "Include discussion questions",
                "Use auditory metaphors and sound-based examples",
                "Suggest verbal mnemonics for memorization"
            ]
        elif primary_style == "reading_writing":
            adapted_content["presentation_hints"] = [
                "Provide detailed written explanations",
                "Include suggested note-taking strategies",
                "Present information in lists and structured formats",
                "Include suggested reading materials"
            ]
        elif primary_style == "kinesthetic":
            adapted_content["presentation_hints"] = [
                "Include hands-on exercises to try",
                "Suggest practical applications of concepts",
                "Break learning into active steps",
                "Use physical metaphors and examples"
            ]
        
        # Add a style-based difficulty adjustment (example of dynamic difficulty)
        confidence = learning_style.get("confidence", 0.5)
        if confidence > 0.7:
            # Strong style preference - tailor strongly
            adapted_content["style_weight"] = "strong"
        else:
            # Mixed preferences - more balanced approach
            adapted_content["style_weight"] = "balanced"
            
        # Add the detected style to the content metadata
        adapted_content["detected_style"] = primary_style
            
        return adapted_content
    
    async def generate_personalized_quiz(self, db, user_id: str, topic: str, 
                                      quiz_generator=None, vector_client=None, 
                                      processor=None) -> Dict[str, Any]:
        """
        Generate a personalized quiz based on user's learning style and progress
        
        Args:
            db: Database session
            user_id: User ID
            topic: Quiz topic
            quiz_generator: QuizGenerator instance
            vector_client: Vector store client
            processor: Message processor
            
        Returns:
            Personalized quiz with style-specific enhancements
        """
        from app.models import repository, models
        from app.utils.context_retrieval import retrieve_topic_context
        
        # Detect learning style
        learning_style = await self.analyze_learning_style(db, user_id)
        primary_style = learning_style.get("primary_style", self.default_style)
        
        # Get progress data to adjust difficulty
        progress = db.query(models.ProgressTracking).filter(
            models.ProgressTracking.user_id == user_id,
            models.ProgressTracking.topic == topic
        ).first()
        
        # Set difficulty based on proficiency
        difficulty = "medium"  # Default
        num_questions = 5  # Default
        
        if progress:
            if progress.proficiency < 0.3:
                difficulty = "easy"
                num_questions = 3  # Fewer questions for beginners
            elif progress.proficiency > 0.7:
                difficulty = "hard"
                num_questions = 7  # More questions for advanced users
        
        # Get context for the quiz
        context_result = await retrieve_topic_context(
            vector_client, 
            topic, 
            min_chunks=8,
            max_chunks=15
        )
        
        context = context_result["context"]
        context_sources = context_result["sources"]
        
        if not context:
            return {"error": "Could not find relevant content for quiz generation"}
        
        # Generate basic quiz
        quiz_result = await quiz_generator.generate_quiz(
            context=context,
            num_questions=num_questions,
            difficulty=difficulty,
            topic=topic,
            client=processor.client,
            model_name=processor.model_name
        )
        
        if "error" in quiz_result and quiz_result["error"]:
            return quiz_result
            
        # Enhance quiz for learning style
        # Add learning style hints to each question
        for question in quiz_result["questions"]:
            if primary_style == "visual":
                question["style_hint"] = "Try to visualize the concept in your mind."
            elif primary_style == "auditory":
                question["style_hint"] = "Try reading the question aloud to yourself."
            elif primary_style == "reading_writing":
                question["style_hint"] = "Consider writing down key points before answering."
            elif primary_style == "kinesthetic":
                question["style_hint"] = "Think about how you would apply this concept practically."
        
        # Add personalization metadata
        quiz_result["metadata"]["personalized"] = True
        quiz_result["metadata"]["learning_style"] = primary_style
        quiz_result["metadata"]["difficulty_level"] = difficulty
        quiz_result["metadata"]["sources"] = context_sources
        
        # Save the personalized quiz
        quiz_db = repository.create_quiz(
            db, 
            user_id=user_id,
            document_id=context_sources[0] if context_sources else "unknown",
            quiz_content=quiz_result
        )
        
        quiz_result["id"] = quiz_db.id
        
        return quiz_result
    
    async def generate_personalized_flashcards(self, db, user_id: str, topic: str,
                                           flashcard_generator=None, vector_client=None,
                                           processor=None) -> Dict[str, Any]:
        """
        Generate personalized flashcards based on user's learning style and progress
        
        Args:
            db: Database session
            user_id: User ID
            topic: Flashcard topic
            flashcard_generator: FlashcardGenerator instance
            vector_client: Vector store client
            processor: Message processor
            
        Returns:
            Personalized flashcards with style-specific enhancements
        """
        from app.models import repository, models
        from app.utils.context_retrieval import retrieve_topic_context
        
        # Detect learning style
        learning_style = await self.analyze_learning_style(db, user_id)
        primary_style = learning_style.get("primary_style", self.default_style)
        
        # Get progress data
        progress = db.query(models.ProgressTracking).filter(
            models.ProgressTracking.user_id == user_id,
            models.ProgressTracking.topic == topic
        ).first()
        
        # Adjust number of flashcards based on proficiency
        num_cards = 8  # Default
        
        if progress:
            if progress.proficiency < 0.3:
                num_cards = 5  # Fewer cards for beginners
            elif progress.proficiency > 0.7:
                num_cards = 10  # More cards for advanced users
        
        # Get context for the flashcards
        context_result = await retrieve_topic_context(
            vector_client, 
            topic, 
            min_chunks=8,
            max_chunks=15
        )
        
        context = context_result["context"]
        context_sources = context_result["sources"]
        
        if not context:
            return {"error": "Could not find relevant content for flashcard generation"}
        
        # Generate basic flashcards
        flashcard_result = await flashcard_generator.generate_flashcards(
            context=context,
            num_cards=num_cards,
            topic=topic,
            client=processor.client,
            model_name=processor.model_name
        )
        
        if "error" in flashcard_result and flashcard_result["error"]:
            return flashcard_result
            
        # Enhance flashcards for learning style
        for card in flashcard_result["cards"]:
            if primary_style == "visual":
                card["style_hint"] = "Visualize an image representing this concept."
            elif primary_style == "auditory":
                card["style_hint"] = "Read the card aloud and discuss the concept."
            elif primary_style == "reading_writing":
                card["style_hint"] = "Write a summary in your own words after reviewing."
            elif primary_style == "kinesthetic":
                card["style_hint"] = "Think of a real-world example where you'd apply this."
        
        # Add personalization metadata
        flashcard_result["metadata"]["personalized"] = True
        flashcard_result["metadata"]["learning_style"] = primary_style
        flashcard_result["metadata"]["sources"] = context_sources
        
        # Save the personalized flashcards
        flashcard_db = repository.create_flashcards(
            db, 
            user_id=user_id,
            document_id=context_sources[0] if context_sources else "unknown",
            flashcard_content=flashcard_result
        )
        
        flashcard_result["id"] = flashcard_db.id
        
        return flashcard_result
    
    async def adapt_tutoring_response(self, response: str, user_id: str, db) -> str:
        """
        Enhance tutoring response based on user's learning style
        
        Args:
            response: Original tutoring response
            user_id: User ID
            db: Database session
            
        Returns:
            Enhanced response with style-specific modifications
        """
        # Detect learning style
        learning_style = await self.analyze_learning_style(db, user_id)
        primary_style = learning_style.get("primary_style", self.default_style)
        
        # Adapt response based on learning style
        if primary_style == "visual":
            # Add visual-oriented suggestions
            enhanced = response + "\n\nVisualization tip: Try creating a mental image or diagram to represent this concept."
        elif primary_style == "auditory":
            # Add auditory-oriented suggestions
            enhanced = response + "\n\nAuditory tip: Try explaining this concept aloud to solidify your understanding."
        elif primary_style == "reading_writing":
            # Add reading/writing-oriented suggestions
            enhanced = response + "\n\nReading/writing tip: Take a moment to write down the key points from this explanation."
        elif primary_style == "kinesthetic":
            # Add kinesthetic-oriented suggestions
            enhanced = response + "\n\nHands-on tip: Think about a practical example where you could apply this concept."
        else:
            enhanced = response
            
        return enhanced
    
    def get_learning_style_strategies(self, learning_style: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recommended strategies based on learning style
        
        Args:
            learning_style: Learning style information
            
        Returns:
            Dict with recommended study strategies
        """
        primary_style = learning_style.get("primary_style", self.default_style)
        
        strategies = {
            "visual": [
                "Use colored highlighters in your notes",
                "Create mind maps for complex topics",
                "Draw diagrams to represent concepts",
                "Watch video explanations when available",
                "Use flashcards with images or symbols"
            ],
            "auditory": [
                "Record and listen to your notes",
                "Discuss topics with study partners",
                "Read important material aloud",
                "Use verbal repetition for memorization",
                "Create musical mnemonics for key concepts"
            ],
            "reading_writing": [
                "Take detailed notes during study sessions",
                "Rewrite key concepts in your own words",
                "Create outlines and structured study guides",
                "Use written repetition for memorization",
                "Summarize what you've learned after each session"
            ],
            "kinesthetic": [
                "Take breaks for physical movement",
                "Use physical objects to represent concepts",
                "Act out processes or sequences",
                "Apply concepts to real-world scenarios",
                "Study while standing or moving around"
            ]
        }
        
        return {
            "primary_style": primary_style,
            "recommended_strategies": strategies.get(primary_style, strategies["reading_writing"])
        }