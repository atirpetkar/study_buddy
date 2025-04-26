# app/core/advanced_study_planner.py
from typing import Dict, Any, List, Optional
import datetime
import json
import re

class AdvancedStudyPlanGenerator:
    """
    Advanced study plan generator that creates personalized study plans
    based on document analysis, learning style, and progress tracking.
    """
    
    def __init__(self):
        self.difficulty_levels = ["beginner", "intermediate", "advanced"]
        self.activity_types = ["reading", "quiz", "flashcards", "practice", "tutorial"]
        
    async def generate_advanced_plan(self, db, user_id: str, 
                                  days: int = 7,
                                  topic_focus: Optional[str] = None,
                                  learning_style: Optional[Dict[str, Any]] = None,
                                  vector_client=None,
                                  processor=None) -> Dict[str, Any]:
        """
        Generate an advanced, personalized study plan
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to plan for
            topic_focus: Optional topic to focus on
            learning_style: Optional pre-loaded learning style data
            vector_client: Vector store client
            processor: Message processor
            
        Returns:
            Dict containing advanced study plan
        """
        from app.models import models, repository
        from app.core.personalization_engine import PersonalizationEngine
        from app.utils.context_retrieval import retrieve_topic_context
        
        pe = PersonalizationEngine()
        
        # Get user progress data
        progress_records = db.query(models.ProgressTracking).filter(
            models.ProgressTracking.user_id == user_id
        ).all()
        
        # Get user profile for available study time
        profile = repository.get_user_profile(db, user_id)
        available_time = "2 hours"  # Default
        
        if profile and "available_study_time" in profile:
            available_time = profile["available_study_time"]
        
        # Determine daily study minutes
        daily_minutes = self._parse_available_time(available_time)
        
        # Get learning style if not provided
        if not learning_style:
            learning_style = await pe.analyze_learning_style(db, user_id)
        
        primary_style = learning_style.get("primary_style", "reading_writing")
        
        # Initialize topics to study
        topics_to_study = []
        
        # If topic focus is provided, prioritize it
        if topic_focus:
            topics_to_study.append({
                "name": topic_focus,
                "priority": "high",
                "proficiency": 0.0,
                "confidence": 0.0
            })
        
        # Add other topics from progress data
        for record in progress_records:
            # Skip the focus topic if already added
            if topic_focus and record.topic == topic_focus:
                # Update proficiency for focus topic
                topics_to_study[0]["proficiency"] = record.proficiency
                topics_to_study[0]["confidence"] = record.confidence
                continue
                
            # Add this topic
            priority = "medium"
            
            # Determine priority - low proficiency or not studied recently gets higher priority
            if record.proficiency < 0.4:
                priority = "high"
            elif (datetime.datetime.utcnow() - record.last_interaction).days > 14:
                priority = "high"
                
            topics_to_study.append({
                "name": record.topic,
                "priority": priority,
                "proficiency": record.proficiency,
                "confidence": record.confidence
            })
        
        # If no topics, create a default plan
        if not topics_to_study:
            return self._generate_default_plan(user_id, days, daily_minutes, primary_style)
        
        # Sort topics by priority (high first), then by proficiency (low first)
        topics_to_study.sort(
            key=lambda x: (0 if x["priority"] == "high" else 1, x["proficiency"])
        )
        
        # Get topic details from document analysis
        if vector_client and processor:
            await self._enhance_topics_with_document_analysis(
                topics_to_study, 
                vector_client, 
                processor
            )
        
        # Generate daily schedules
        schedule = []
        now = datetime.datetime.utcnow()
        
        # Get topic distribution - how many topics to cover each day
        topics_per_day = min(3, len(topics_to_study))
        
        # Distribute topics across days
        for day in range(days):
            current_date = now + datetime.timedelta(days=day)
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Determine day's topics
            day_topics = []
            remaining_minutes = daily_minutes
            
            for i in range(min(topics_per_day, len(topics_to_study))):
                # Rotate topics day by day, but always include high priority ones
                topic_idx = (i + day) % len(topics_to_study)
                topic = topics_to_study[topic_idx]
                
                # Skip if we've run out of time
                if remaining_minutes < 10:
                    break
                    
                # Allocate time for this topic - higher priority gets more time
                if topic["priority"] == "high":
                    topic_minutes = min(remaining_minutes, daily_minutes // 2)
                else:
                    topic_minutes = min(remaining_minutes, daily_minutes // 3)
                    
                remaining_minutes -= topic_minutes
                
                # Generate activities for this topic
                activities = self._generate_activities_for_topic(
                    topic,
                    topic_minutes,
                    primary_style,
                    day_of_week=current_date.strftime("%A")
                )
                
                # Create topic entry
                day_topics.append({
                    "topic": topic["name"],
                    "activities": activities,
                    "total_duration": sum(a["duration"] for a in activities),
                    "priority": topic["priority"],
                    "key_concepts": topic.get("key_concepts", [])
                })
            
            # Add to schedule
            schedule.append({
                "date": date_str,
                "day_of_week": current_date.strftime("%A"),
                "topics": day_topics,
                "total_duration": sum(topic["total_duration"] for topic in day_topics),
                "style_recommendations": self._get_style_recommendations(primary_style)
            })
        
        # Generate overall weekly goals and key learning objectives
        weekly_goals = self._generate_advanced_goals(topics_to_study)
        
        # Create the final plan
        plan = {
            "user_id": user_id,
            "generated_at": now.isoformat(),
            "learning_style": primary_style,
            "daily_study_time": daily_minutes,
            "schedule": schedule,
            "weekly_goals": weekly_goals,
            "focus_areas": [topic["name"] for topic in topics_to_study if topic["priority"] == "high"],
            "document_insights": self._generate_document_insights(topics_to_study)
        }
        
        # Save the plan
        saved_plan = repository.create_study_plan(db, user_id, plan)
        
        return {
            "plan_id": saved_plan.id,
            "plan": plan
        }
    
    async def _enhance_topics_with_document_analysis(self, topics: List[Dict[str, Any]], 
                                                 vector_client, processor) -> None:
        """
        Enhance topic data with document analysis
        
        Args:
            topics: List of topic data dicts
            vector_client: Vector store client
            processor: Message processor
            
        Returns:
            None (modifies topics in-place)
        """
        from app.utils.context_retrieval import retrieve_topic_context
        
        for topic in topics:
            try:
                topic_name = topic["name"]
                
                # Get context for this topic
                context_result = await retrieve_topic_context(
                    vector_client, 
                    topic_name, 
                    min_chunks=3,
                    max_chunks=5
                )
                
                context = context_result["context"]
                
                if not context:
                    continue
                    
                # Extract key concepts
                prompt = f"""
                Extract 3-5 key concepts from the following text about {topic_name}.
                Return a comma-separated list of concepts only, without numbering or explanations.
                
                TEXT:
                {context[:1500]}
                
                KEY CONCEPTS:
                """
                
                messages = [
                    {"role": "system", "content": "You extract key concepts from educational content."},
                    {"role": "user", "content": prompt}
                ]
                
                response = await processor.client.chat.completions.create(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=100,
                    model=processor.model_name
                )
                
                concepts_text = response.choices[0].message.content
                concepts = [concept.strip() for concept in concepts_text.split(',')]
                
                # Determine complexity level
                complexity_prompt = f"""
                On a scale from 1-5 (1 being elementary, 5 being advanced), 
                rate the complexity level of content about {topic_name} below.
                Return only the numeric rating.
                
                CONTENT:
                {context[:1000]}
                
                COMPLEXITY RATING:
                """
                
                messages = [
                    {"role": "system", "content": "You rate the complexity of educational content."},
                    {"role": "user", "content": complexity_prompt}
                ]
                
                response = await processor.client.chat.completions.create(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=10,
                    model=processor.model_name
                )
                
                complexity_text = response.choices[0].message.content
                # Extract just the number
                complexity_match = re.search(r'\d+', complexity_text)
                complexity = int(complexity_match.group(0)) if complexity_match else 3
                
                # Add to topic data
                topic["key_concepts"] = concepts[:5]  # Limit to 5 concepts
                topic["complexity"] = complexity
                topic["sources"] = context_result["sources"]
                
            except Exception as e:
                print(f"Error enhancing topic {topic['name']} with document analysis: {e}")
                # Continue with other topics if one fails
    
    def _parse_available_time(self, time_str: str) -> int:
        """
        Parse available study time string into minutes per day
        
        Args:
            time_str: String describing available time (e.g., '2 hours', '30 minutes')
            
        Returns:
            Minutes per day for studying
        """
        time_str = time_str.lower()
        
        # Try to parse hours and minutes
        hours_match = re.search(r'(\d+)\s*hour', time_str)
        minutes_match = re.search(r'(\d+)\s*minute', time_str)
        
        total_minutes = 0
        
        if hours_match:
            total_minutes += int(hours_match.group(1)) * 60
            
        if minutes_match:
            total_minutes += int(minutes_match.group(1))
            
        # Default if parsing fails
        if total_minutes == 0:
            # Try to just extract any number
            any_number = re.search(r'(\d+)', time_str)
            if any_number:
                # Assume hours if it's a small number, minutes otherwise
                num = int(any_number.group(1))
                if num < 24:
                    total_minutes = num * 60
                else:
                    total_minutes = num
        
        # Fallback default
        if total_minutes == 0:
            total_minutes = 120  # 2 hours default
            
        return total_minutes
    
    def _generate_default_plan(self, user_id: str, days: int, daily_minutes: int, learning_style: str) -> Dict[str, Any]:
        """
        Generate a default plan for new users
        
        Args:
            user_id: User ID
            days: Number of days to plan for
            daily_minutes: Minutes available per day
            learning_style: Primary learning style
            
        Returns:
            Default study plan
        """
        now = datetime.datetime.utcnow()
        
        # Default topics for new users
        default_topics = [
            "Study Planning and Organization",
            "Effective Learning Techniques",
            "Document Upload and Management"
        ]
        
        # Empty schedule for days
        schedule = []
        for day in range(days):
            current_date = now + datetime.timedelta(days=day)
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Pick a topic for this day
            topic = default_topics[day % len(default_topics)]
            
            # Get activities
            activities = [
                {
                    "type": "tutorial",
                    "duration": 20,
                    "description": f"Introduction to {topic}"
                },
                {
                    "type": "exploration",
                    "duration": 20,
                    "description": "Explore the Study Buddy features"
                }
            ]
            
            topics = [{
                "topic": topic,
                "activities": activities,
                "total_duration": sum(a["duration"] for a in activities)
            }]
            
            schedule.append({
                "date": date_str,
                "day_of_week": current_date.strftime("%A"),
                "topics": topics,
                "total_duration": sum(topic["total_duration"] for topic in topics),
                "suggestion": "Upload study materials and take initial quizzes to get personalized recommendations",
                "style_recommendations": self._get_style_recommendations(learning_style)
            })
        
        return {
            "plan_id": "default_" + str(now.timestamp()),
            "plan": {
                "user_id": user_id,
                "generated_at": now.isoformat(),
                "learning_style": learning_style,
                "daily_study_time": daily_minutes,
                "schedule": schedule,
                "weekly_goals": [
                    "Upload your study materials",
                    "Take diagnostic quizzes to establish baseline knowledge",
                    "Complete your learning profile",
                    "Explore the Study Buddy features"
                ],
                "focus_areas": [],
                "document_insights": []
            }
        }
    
    def _generate_activities_for_topic(self, topic: Dict[str, Any], 
                                      available_minutes: int,
                                      learning_style: str,
                                      day_of_week: str) -> List[Dict[str, Any]]:
        """
        Generate activities for a topic based on proficiency, style, and time
        
        Args:
            topic: Topic data
            available_minutes: Minutes available for this topic
            learning_style: Primary learning style
            day_of_week: Current day of week
            
        Returns:
            List of activities
        """
        activities = []
        proficiency = topic.get("proficiency", 0.5)
        
        # Adjust activity types based on learning style
        style_activities = {
            "visual": ["flashcards", "diagram", "video"],
            "auditory": ["discussion", "audio", "explain"],
            "reading_writing": ["reading", "summary", "notes"],
            "kinesthetic": ["practice", "example", "application"]
        }
        
        preferred_activities = style_activities.get(learning_style, ["reading", "flashcards", "quiz"])
        
        # Adjust activity mix based on proficiency
        if proficiency < 0.3:
            # Beginner - focus on fundamentals
            if "reading" in preferred_activities or learning_style == "reading_writing":
                activities.append({
                    "type": "reading",
                    "duration": min(20, available_minutes),
                    "description": f"Read introduction to {topic['name']}"
                })
                available_minutes -= activities[-1]["duration"]
            
            if available_minutes >= 15 and "flashcards" in preferred_activities:
                activities.append({
                    "type": "flashcards",
                    "duration": min(15, available_minutes),
                    "description": f"Review basic {topic['name']} flashcards"
                })
                available_minutes -= activities[-1]["duration"]
                
            if available_minutes >= 20:
                activities.append({
                    "type": "tutorial",
                    "duration": min(20, available_minutes),
                    "description": f"Complete tutorial on {topic['name']} fundamentals"
                })
                available_minutes -= activities[-1]["duration"]
                
        elif proficiency < 0.7:
            # Intermediate - mix of practice and consolidation
            if available_minutes >= 15:
                activities.append({
                    "type": "quiz",
                    "duration": min(15, available_minutes),
                    "description": f"Take practice quiz on {topic['name']}"
                })
                available_minutes -= activities[-1]["duration"]
                
            if available_minutes >= 15 and any(act in preferred_activities for act in ["practice", "example", "application"]):
                activities.append({
                    "type": "practice",
                    "duration": min(20, available_minutes),
                    "description": f"Work through practice problems on {topic['name']}"
                })
                available_minutes -= activities[-1]["duration"]
                
            if available_minutes >= 10:
                activities.append({
                    "type": "flashcards",
                    "duration": min(10, available_minutes),
                    "description": f"Review {topic['name']} flashcards"
                })
                available_minutes -= activities[-1]["duration"]
                
        else:
            # Advanced - focus on mastery and connections
            if available_minutes >= 20:
                activities.append({
                    "type": "advanced quiz",
                    "duration": min(20, available_minutes),
                    "description": f"Take advanced quiz on {topic['name']}"
                })
                available_minutes -= activities[-1]["duration"]
                
            if available_minutes >= 15:
                activities.append({
                    "type": "connections",
                    "duration": min(15, available_minutes),
                    "description": f"Explore connections between {topic['name']} and related topics"
                })
                available_minutes -= activities[-1]["duration"]
                
            if available_minutes >= 10:
                activities.append({
                    "type": "flashcards",
                    "duration": min(10, available_minutes),
                    "description": f"Quick review of {topic['name']} advanced flashcards"
                })
                available_minutes -= activities[-1]["duration"]
                
        # Add key concepts activity if we have them
        if topic.get("key_concepts") and available_minutes >= 15:
            concept = topic["key_concepts"][0]
            activities.append({
                "type": "concept focus",
                "duration": min(15, available_minutes),
                "description": f"Deep dive into '{concept}'"
            })
            available_minutes -= activities[-1]["duration"]
            
        # Add style-specific activity if time permits
        if available_minutes >= 15:
            if learning_style == "visual":
                activities.append({
                    "type": "visualization",
                    "duration": min(15, available_minutes),
                    "description": f"Create visual representations of {topic['name']} concepts"
                })
            elif learning_style == "auditory":
                activities.append({
                    "type": "discussion",
                    "duration": min(15, available_minutes),
                    "description": f"Record yourself explaining {topic['name']} concepts"
                })
            elif learning_style == "reading_writing":
                activities.append({
                    "type": "summary",
                    "duration": min(15, available_minutes),
                    "description": f"Write summary notes on {topic['name']}"
                })
            elif learning_style == "kinesthetic":
                activities.append({
                    "type": "application",
                    "duration": min(15, available_minutes),
                    "description": f"Apply {topic['name']} to a real-world example"
                })
                
        # Add spaced repetition on weekends
        if day_of_week in ["Saturday", "Sunday"] and available_minutes >= 15:
            activities.append({
                "type": "review",
                "duration": min(15, available_minutes),
                "description": f"Comprehensive review of {topic['name']}"
            })
            
        return activities
    
    def _get_style_recommendations(self, learning_style: str) -> List[str]:
        """
        Get study recommendations based on learning style
        
        Args:
            learning_style: Primary learning style
            
        Returns:
            List of style-specific recommendations
        """
        recommendations = {
            "visual": [
                "Use color coding in your notes",
                "Create mind maps or diagrams",
                "Watch educational videos when available",
                "Visualize concepts as images"
            ],
            "auditory": [
                "Read important materials aloud",
                "Discuss concepts with others",
                "Record and listen to your notes",
                "Use verbal repetition for memorization"
            ],
            "reading_writing": [
                "Take detailed notes",
                "Rewrite key concepts in your own words",
                "Create lists and outlines",
                "Write summaries after each session"
            ],
            "kinesthetic": [
                "Take short walking breaks",
                "Use physical objects to represent concepts",
                "Act out processes when possible",
                "Apply concepts to real-world scenarios"
            ]
        }
        
        return recommendations.get(learning_style, recommendations["reading_writing"])
    
    def _generate_advanced_goals(self, topics: List[Dict[str, Any]]) -> List[str]:
        """
        Generate advanced weekly goals based on topics
        
        Args:
            topics: List of topic data
            
        Returns:
            List of weekly goals
        """
        goals = []
        
        # Add mastery goals for low proficiency topics
        low_prof_topics = [topic for topic in topics if topic.get("proficiency", 0) < 0.4]
        if low_prof_topics:
            topics_str = ", ".join([t["name"] for t in low_prof_topics[:2]])
            goals.append(f"Master the fundamentals of {topics_str}")
        
        # Add practice goals for medium proficiency topics
        med_prof_topics = [topic for topic in topics if 0.4 <= topic.get("proficiency", 0) < 0.7]
        if med_prof_topics:
            topics_str = ", ".join([t["name"] for t in med_prof_topics[:2]])
            goals.append(f"Practice applying concepts in {topics_str}")
        
        # Add advanced goals for high proficiency topics
        high_prof_topics = [topic for topic in topics if topic.get("proficiency", 0) >= 0.7]
        if high_prof_topics:
            topics_str = ", ".join([t["name"] for t in high_prof_topics[:2]])
            goals.append(f"Deepen understanding of advanced aspects of {topics_str}")
        
        # Add general goals
        goals.append("Complete all scheduled study sessions")
        goals.append("Review progress at the end of the week")
        
        # Add key concept goals if available
        all_concepts = []
        for topic in topics:
            if topic.get("key_concepts"):
                all_concepts.extend(topic["key_concepts"][:2])  # Take top 2 from each topic
                
        if all_concepts:
            concepts_str = ", ".join(all_concepts[:3])  # Limit to 3 concepts total
            goals.append(f"Master these key concepts: {concepts_str}")
        
        return goals
    
    def _generate_document_insights(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate insights based on document analysis
        
        Args:
            topics: List of topic data
            
        Returns:
            List of document insights
        """
        insights = []
        
        # Generate insights about topic complexity
        for topic in topics:
            if not topic.get("key_concepts") or not topic.get("complexity"):
                continue
                
            complexity = topic.get("complexity", 3)
            complexity_desc = "basic" if complexity <= 2 else "intermediate" if complexity <= 4 else "advanced"
            
            insights.append({
                "topic": topic["name"],
                "type": "complexity",
                "description": f"This topic contains {complexity_desc} level content",
                "key_concepts": topic.get("key_concepts", [])[:3],
                "recommendation": self._get_complexity_recommendation(complexity)
            })
        
        # Generate insights about topic connections
        all_topics = [t["name"] for t in topics]
        if len(all_topics) >= 2:
            for i in range(min(3, len(topics))):
                if i+1 < len(topics):
                    insights.append({
                        "type": "connection",
                        "description": f"Consider exploring connections between {topics[i]['name']} and {topics[i+1]['name']}",
                        "recommended_activity": "Comparative study session"
                    })
        
        return insights
    
    def _get_complexity_recommendation(self, complexity: int) -> str:
        """
        Get recommendation based on content complexity
        
        Args:
            complexity: Complexity rating (1-5)
            
        Returns:
            Recommendation string
        """
        if complexity <= 2:
            return "Focus on building a strong foundation before advancing"
        elif complexity <= 4:
            return "Balance theory with practical applications"
        else:
            return "Break down complex topics into smaller parts for better understanding"