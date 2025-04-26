# app/tests/integration_tests.py
import asyncio
import os
import time
import sys
from typing import Dict, Any, List

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.agent import get_message_processor
from app.core.vector_store import get_vector_store_client
from app.core.quiz_generator import QuizGenerator
from app.core.flashcard_generator import FlashcardGenerator
from app.core.personalization_engine import PersonalizationEngine
from app.utils.context_retrieval import retrieve_topic_context, retrieve_enhanced_context
from app.utils.optimization import timing_decorator, response_time_monitor, embedding_cache

class IntegrationTests:
    """Comprehensive integration tests for Study Buddy Agent"""
    
    def __init__(self):
        self.results = {}
        self.vector_client = None
        self.processor = None
        self.quiz_gen = None
        self.flashcard_gen = None
        self.personalization = None
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("\n===== STUDY BUDDY INTEGRATION TESTS =====")
        
        # Initialize components
        success = await self.initialize_components()
        if not success:
            print("❌ Component initialization failed. Aborting tests.")
            return False
            
        # Run individual tests
        await self.test_vector_store()
        await self.test_context_retrieval()
        await self.test_quiz_generation()
        await self.test_flashcard_generation()
        await self.test_tutoring()
        await self.test_personalization()
        await self.test_end_to_end()
        
        # Summarize results
        self.summarize_results()
        
        return all(result.get("passed", False) for result in self.results.values())
    
    @timing_decorator
    async def initialize_components(self):
        """Initialize all components needed for testing"""
        try:
            print("\nInitializing components...")
            
            # Initialize vector store
            self.vector_client = get_vector_store_client()
            print(f"Vector store initialized with {self.vector_client.index.ntotal} vectors")
            
            # Initialize message processor
            self.processor = get_message_processor()
            print(f"Message processor initialized with model: {self.processor.model_name}")
            
            # Initialize quiz generator
            self.quiz_gen = QuizGenerator()
            print("Quiz generator initialized")
            
            # Initialize flashcard generator
            self.flashcard_gen = FlashcardGenerator()
            print("Flashcard generator initialized")
            
            # Initialize personalization engine
            self.personalization = PersonalizationEngine()
            print("Personalization engine initialized")
            
            print("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Component initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @timing_decorator
    async def test_vector_store(self):
        """Test vector store functionality"""
        test_name = "vector_store"
        print(f"\n----- Testing {test_name} -----")
        
        try:
            # Skip test if no vectors
            if self.vector_client.index.ntotal == 0:
                print("No vectors in store. This test will be skipped.")
                self.results[test_name] = {
                    "passed": None,
                    "message": "Skipped - no vectors in store"
                }
                return
                
            # Simple vector search test
            query = "machine learning basics"
            timer_id = response_time_monitor.start_timer("vector_search")
            
            results = await self.vector_client.search(query, top_k=3)
            
            duration = response_time_monitor.end_timer(timer_id)
            print(f"Search completed in {duration:.2f} seconds")
            
            if not results or not results.get("results"):
                raise Exception("Search returned no results")
                
            print(f"Search returned {len(results['results'])} results")
            
            # Test passed if we got results
            self.results[test_name] = {
                "passed": True,
                "message": f"Search returned {len(results['results'])} results in {duration:.2f} seconds",
                "duration": duration
            }
            print(f"✅ {test_name} test passed")
            
        except Exception as e:
            self.results[test_name] = {
                "passed": False,
                "message": f"Error: {str(e)}"
            }
            print(f"❌ {test_name} test failed: {e}")
            import traceback
            traceback.print_exc()
    
    @timing_decorator
    async def test_context_retrieval(self):
        """Test context retrieval functionality"""
        test_name = "context_retrieval"
        print(f"\n----- Testing {test_name} -----")
        
        try:
            # Skip test if no vectors
            if self.vector_client.index.ntotal == 0:
                print("No vectors in store. This test will be skipped.")
                self.results[test_name] = {
                    "passed": None,
                    "message": "Skipped - no vectors in store"
                }
                return
                
            # Test topic context retrieval
            topic = "machine learning"
            
            timer_id = response_time_monitor.start_timer("topic_context")
            
            context_result = await retrieve_topic_context(
                self.vector_client, 
                topic, 
                min_chunks=3,
                max_chunks=7
            )
            
            duration = response_time_monitor.end_timer(timer_id)
            print(f"Topic context retrieval completed in {duration:.2f} seconds")
            
            if not context_result or not context_result.get("context"):
                raise Exception("Context retrieval returned no context")
                
            context_length = len(context_result["context"].split())
            sources_count = len(context_result.get("sources", []))
            
            print(f"Retrieved {context_length} words from {sources_count} sources")
            
            # Test enhanced context retrieval
            query = "What is supervised learning?"
            
            timer_id = response_time_monitor.start_timer("enhanced_context")
            
            enhanced_result = await retrieve_enhanced_context(
                self.vector_client,
                query
            )
            
            enhanced_duration = response_time_monitor.end_timer(timer_id)
            print(f"Enhanced context retrieval completed in {enhanced_duration:.2f} seconds")
            
            if not enhanced_result or not enhanced_result.get("results"):
                raise Exception("Enhanced context retrieval returned no results")
                
            results_count = len(enhanced_result["results"])
            
            print(f"Enhanced retrieval returned {results_count} results")
            
            # Test passed if both retrievals worked
            self.results[test_name] = {
                "passed": True,
                "message": f"Retrieved {context_length} words from {sources_count} sources",
                "duration": duration,
                "context_length": context_length
            }
            print(f"✅ {test_name} test passed")
            
        except Exception as e:
            self.results[test_name] = {
                "passed": False,
                "message": f"Error: {str(e)}"
            }
            print(f"❌ {test_name} test failed: {e}")
            import traceback
            traceback.print_exc()
    
    @timing_decorator
    async def test_quiz_generation(self):
        """Test quiz generation functionality"""
        test_name = "quiz_generation"
        print(f"\n----- Testing {test_name} -----")
        
        try:
            # Use a simple context for testing
            if self.results.get("context_retrieval", {}).get("passed"):
                # Use previously retrieved context
                topic = "machine learning"
                context_result = await retrieve_topic_context(
                    self.vector_client, 
                    topic, 
                    min_chunks=3,
                    max_chunks=7
                )
                context = context_result["context"]
            else:
                # Use a test context if no retrieved context
                context = """
                Machine learning is a field of artificial intelligence that uses algorithms to learn from data.
                There are three main types of machine learning:
                1. Supervised Learning: Uses labeled data to train models. Examples include classification and regression.
                2. Unsupervised Learning: Works with unlabeled data to find patterns. Examples include clustering and dimensionality reduction.
                3. Reinforcement Learning: Involves an agent learning through trial and error in an environment.
                """
                
            print(f"Generating quiz with context of {len(context.split())} words")
            
            # Generate quiz
            timer_id = response_time_monitor.start_timer("quiz_generation")
            
            quiz = await self.quiz_gen.generate_quiz(
                context=context,
                num_questions=2,  # Small for testing
                difficulty="medium",
                topic="machine learning",
                client=self.processor.client,
                model_name=self.processor.model_name
            )
            
            duration = response_time_monitor.end_timer(timer_id)
            print(f"Quiz generation completed in {duration:.2f} seconds")
            
            if not quiz or not quiz.get("questions"):
                raise Exception("Quiz generation returned no questions")
                
            question_count = len(quiz["questions"])
            
            print(f"Generated {question_count} questions")
            
            # Print sample question
            if question_count > 0:
                sample_q = quiz["questions"][0]
                print(f"Sample question: {sample_q['text']}")
                
            # Test passed if we got questions
            self.results[test_name] = {
                "passed": question_count > 0,
                "message": f"Generated {question_count} questions in {duration:.2f} seconds",
                "duration": duration,
                "questions": question_count
            }
            
            if question_count > 0:
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed: No questions generated")
            
        except Exception as e:
            self.results[test_name] = {
                "passed": False,
                "message": f"Error: {str(e)}"
            }
            print(f"❌ {test_name} test failed: {e}")
            import traceback
            traceback.print_exc()
    
    @timing_decorator
    async def test_flashcard_generation(self):
        """Test flashcard generation functionality"""
        test_name = "flashcard_generation"
        print(f"\n----- Testing {test_name} -----")
        
        try:
            # Use a simple context for testing
            if self.results.get("context_retrieval", {}).get("passed"):
                # Use previously retrieved context
                topic = "machine learning"
                context_result = await retrieve_topic_context(
                    self.vector_client, 
                    topic, 
                    min_chunks=3,
                    max_chunks=7
                )
                context = context_result["context"]
            else:
                # Use a test context if no retrieved context
                context = """
                Machine learning is a field of artificial intelligence that uses algorithms to learn from data.
                There are three main types of machine learning:
                1. Supervised Learning: Uses labeled data to train models. Examples include classification and regression.
                2. Unsupervised Learning: Works with unlabeled data to find patterns. Examples include clustering and dimensionality reduction.
                3. Reinforcement Learning: Involves an agent learning through trial and error in an environment.
                """
                
            print(f"Generating flashcards with context of {len(context.split())} words")
            
            # Generate flashcards
            timer_id = response_time_monitor.start_timer("flashcard_generation")
            
            flashcards = await self.flashcard_gen.generate_flashcards(
                context=context,
                num_cards=3,  # Small for testing
                topic="machine learning",
                client=self.processor.client,
                model_name=self.processor.model_name
            )
            
            duration = response_time_monitor.end_timer(timer_id)
            print(f"Flashcard generation completed in {duration:.2f} seconds")
            
            if not flashcards or not flashcards.get("cards"):
                raise Exception("Flashcard generation returned no cards")
                
            card_count = len(flashcards["cards"])
            
            print(f"Generated {card_count} flashcards")
            
            # Print sample flashcard
            if card_count > 0:
                sample_card = flashcards["cards"][0]
                print(f"Sample flashcard front: {sample_card['front']}")
                
            # Test passed if we got flashcards
            self.results[test_name] = {
                "passed": card_count > 0,
                "message": f"Generated {card_count} flashcards in {duration:.2f} seconds",
                "duration": duration,
                "cards": card_count
            }
            
            if card_count > 0:
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed: No flashcards generated")
            
        except Exception as e:
            self.results[test_name] = {
                "passed": False,
                "message": f"Error: {str(e)}"
            }
            print(f"❌ {test_name} test failed: {e}")
            import traceback
            traceback.print_exc()
    
    @timing_decorator
    async def test_tutoring(self):
        """Test tutoring functionality"""
        test_name = "tutoring"
        print(f"\n----- Testing {test_name} -----")
        
        try:
            # Test tutoring response
            user_id = "test_user_integration"
            question = "Help me understand the difference between supervised and unsupervised learning"
            
            timer_id = response_time_monitor.start_timer("tutoring_response")
            
            tutoring_result = await self.processor.process_message(
                user_id=user_id,
                message=question,
                mode="tutor",
                vector_search_client=self.vector_client
            )
            
            duration = response_time_monitor.end_timer(timer_id)
            print(f"Tutoring response completed in {duration:.2f} seconds")
            
            if not tutoring_result or not tutoring_result.get("response"):
                raise Exception("Tutoring response returned no response")
                
            response_length = len(tutoring_result["response"].split())
            
            print(f"Generated tutoring response with {response_length} words")
            
            # Test passed if we got a response
            self.results[test_name] = {
                "passed": response_length > 0,
                "message": f"Generated tutoring response with {response_length} words in {duration:.2f} seconds",
                "duration": duration,
                "response_length": response_length
            }
            
            if response_length > 0:
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed: No response generated")
            
        except Exception as e:
            self.results[test_name] = {
                "passed": False,
                "message": f"Error: {str(e)}"
            }
            print(f"❌ {test_name} test failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Modified test_personalization method for app/tests/integration_tests.py

    @timing_decorator
    async def test_personalization(self):
        """Test personalization functionality with mock data"""
        test_name = "personalization"
        print(f"\n----- Testing {test_name} -----")
        
        try:
            # Since this is just an integration test, we'll use mock data
            user_id = "test_user_integration"
            
            # Mock conversation history for learning style detection
            conversation_history = [
                {"role": "user", "content": "I need to see visual examples to understand this."},
                {"role": "assistant", "content": "I understand you prefer visual learning. Let me explain..."},
                {"role": "user", "content": "Can you show me a diagram of how this works?"},
                {"role": "user", "content": "I like to see things mapped out visually."}
            ]
            
            # Test learning style detection - NOTE: No await here as this is not an async method
            timer_id = response_time_monitor.start_timer("learning_style_detection")
            
            # This would normally use the database, but for testing we'll just use the method directly
            # Remove the await since _analyze_text_for_style is not an async method
            learning_style = self.personalization._analyze_text_for_style(conversation_history)
            
            duration = response_time_monitor.end_timer(timer_id)
            print(f"Learning style detection completed in {duration:.2f} seconds")
            
            # Make sure we got a result
            if not learning_style:
                raise Exception("Learning style detection returned no results")
                
            # Create a simulated learning style result
            style_result = {
                "primary_style": max(learning_style.items(), key=lambda x: x[1])[0] if learning_style else "visual",
                "scores": learning_style
            }
            
            print(f"Detected primary learning style: {style_result['primary_style']}")
            
            # Test content adaptation - this method is async so we keep the await
            content = {
                "type": "quiz",
                "questions": [
                    {
                        "text": "What is machine learning?",
                        "options": {"A": "Option A", "B": "Option B"}
                    }
                ]
            }
            
            adapted_content = await self.personalization.adapt_content_for_style(
                content, 
                {"primary_style": style_result["primary_style"]}
            )
            
            # Check if adaptation worked
            adapted = "presentation_hints" in adapted_content
            
            print(f"Content adaptation {'succeeded' if adapted else 'failed'}")
            
            # Test passed if both detection and adaptation worked
            self.results[test_name] = {
                "passed": adapted and style_result["primary_style"] is not None,
                "message": f"Detected '{style_result['primary_style']}' style and adapted content",
                "duration": duration,
                "style": style_result["primary_style"]
            }
            
            if adapted and style_result["primary_style"] is not None:
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed: Style detection or adaptation failed")
            
        except Exception as e:
            self.results[test_name] = {
                "passed": False,
                "message": f"Error: {str(e)}"
            }
            print(f"❌ {test_name} test failed: {e}")
            import traceback
            traceback.print_exc()
    
    @timing_decorator
    async def test_end_to_end(self):
        """Test full end-to-end flow"""
        test_name = "end_to_end"
        print(f"\n----- Testing {test_name} -----")
        
        try:
            # Define test parameters
            user_id = "test_user_integration"
            topic = "machine learning"
            
            # Step 1: Get context
            print("\nStep 1: Context Retrieval")
            context_result = await retrieve_topic_context(
                self.vector_client, 
                topic, 
                min_chunks=3,
                max_chunks=7
            )
            
            if not context_result or not context_result.get("context"):
                print("No context found. Using sample text.")
                context = """
                Machine learning is a field of artificial intelligence that uses algorithms to learn from data.
                There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning.
                """
            else:
                context = context_result["context"]
                print(f"Retrieved context with {len(context.split())} words")
            
            # Step 2: Generate quiz
            print("\nStep 2: Quiz Generation")
            quiz = await self.quiz_gen.generate_quiz(
                context=context,
                num_questions=1,  # Minimal for testing
                difficulty="medium",
                topic=topic,
                client=self.processor.client,
                model_name=self.processor.model_name
            )
            
            if not quiz or not quiz.get("questions"):
                print("Quiz generation failed")
                quiz_success = False
            else:
                print(f"Generated {len(quiz['questions'])} questions")
                quiz_success = True
            
            # Step 3: Generate flashcards
            print("\nStep 3: Flashcard Generation")
            flashcards = await self.flashcard_gen.generate_flashcards(
                context=context,
                num_cards=1,  # Minimal for testing
                topic=topic,
                client=self.processor.client,
                model_name=self.processor.model_name
            )
            
            if not flashcards or not flashcards.get("cards"):
                print("Flashcard generation failed")
                flashcard_success = False
            else:
                print(f"Generated {len(flashcards['cards'])} flashcards")
                flashcard_success = True
            
            # Step 4: Tutoring response
            print("\nStep 4: Tutoring")
            tutoring_result = await self.processor.process_message(
                user_id=user_id,
                message=f"Help me understand {topic}",
                mode="tutor",
                vector_search_client=self.vector_client
            )
            
            if not tutoring_result or not tutoring_result.get("response"):
                print("Tutoring response failed")
                tutoring_success = False
            else:
                print("Tutoring response generated successfully")
                tutoring_success = True
            
            # Overall success
            all_successful = quiz_success and flashcard_success and tutoring_success
            
            # Test passed if all steps worked
            self.results[test_name] = {
                "passed": all_successful,
                "message": "End-to-end test completed" + 
                           (" with all steps successful" if all_successful else " with some steps failing"),
                "steps_successful": {
                    "quiz": quiz_success,
                    "flashcard": flashcard_success,
                    "tutoring": tutoring_success
                }
            }
            
            if all_successful:
                print(f"✅ {test_name} test passed - All components working together")
            else:
                print(f"❌ {test_name} test failed - Some components not working together")
            
        except Exception as e:
            self.results[test_name] = {
                "passed": False,
                "message": f"Error: {str(e)}"
            }
            print(f"❌ {test_name} test failed: {e}")
            import traceback
            traceback.print_exc()
    
    def summarize_results(self):
        """Summarize test results"""
        print("\n===== TEST RESULTS SUMMARY =====")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result.get("passed", False))
        skipped_tests = sum(1 for result in self.results.values() if result.get("passed") is None)
        failed_tests = total_tests - passed_tests - skipped_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Skipped: {skipped_tests}")
        
        # Print result details
        print("\nTest Details:")
        for test_name, result in self.results.items():
            status = "✅ PASSED" if result.get("passed", False) else "❌ FAILED" if result.get("passed") is not None else "⏭ SKIPPED"
            message = result.get("message", "No message")
            duration = result.get("duration", "N/A")
            
            print(f"{status} - {test_name}: {message}")
            if result.get("duration"):
                print(f"  Duration: {result['duration']:.2f} seconds")
        
        # Print performance stats
        print("\nPerformance Statistics:")
        performance_stats = response_time_monitor.get_stats()
        for component, stats in performance_stats.items():
            print(f"{component}: Avg {stats['avg_time']:.2f}s, Max {stats['max_time']:.2f}s, Calls: {stats['count']}")
        
        # Print cache stats
        print("\nEmbedding Cache Statistics:")
        cache_stats = embedding_cache.get_stats()
        print(f"Size: {cache_stats['size']}/{cache_stats['max_size']}")
        print(f"Hit Rate: {cache_stats['hit_rate']*100:.1f}% ({cache_stats['hits']} hits, {cache_stats['misses']} misses)")
        
        # Print final result
        overall_success = passed_tests == total_tests - skipped_tests
        print("\n===== END-TO-END TEST", "COMPLETE - ALL SYSTEMS OPERATIONAL" if overall_success else "FAILED - SOME SYSTEMS NOT OPERATIONAL", "=====")

if __name__ == "__main__":
    # Run tests
    tests = IntegrationTests()
    asyncio.run(tests.run_all_tests())