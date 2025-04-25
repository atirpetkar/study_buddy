# app/core/quiz_generator.py - Final fixed version
from typing import List, Dict, Any
import re
import json

class QuizGenerator:
    """Service for generating quizzes from document content"""
    
    def __init__(self):
        self.question_types = [
            "multiple_choice",  # Default type
            "true_false",
            "fill_blank"
        ]
    
    async def generate_quiz(self, 
                           context: str, 
                           num_questions: int = 5,
                           difficulty: str = "medium", 
                           topic: str = None,
                           client=None,
                           model_name: str = None) -> Dict[str, Any]:
        """
        Generate a quiz based on the provided context
        
        Args:
            context: Text from retrieved documents
            num_questions: Number of questions to generate
            difficulty: easy, medium, or hard
            topic: Optional specific topic to focus on
            client: LLM client
            model_name: LLM model name
            
        Returns:
            Dict containing quiz questions and metadata
        """
        if not context or not client:
            print("Missing context or client in generate_quiz")
            return {"questions": [], "metadata": {}, "error": "Missing context or LLM client"}
        
        # Build prompt for quiz generation
        prompt = self._build_quiz_prompt(context, num_questions, difficulty, topic)
        
        try:
            print(f"Sending prompt to model {model_name} - prompt length: {len(prompt)}")
            
            # Call the LLM to generate quiz
            messages = [
                {"role": "system", "content": "You are a quiz generation assistant specialized in creating multiple-choice educational quizzes. Follow the requested format exactly."},
                {"role": "user", "content": prompt}
            ]
            
            response = await client.chat.completions.create(
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                model=model_name
            )
            
            quiz_text = response.choices[0].message.content
            print(f"Received response - length: {len(quiz_text)}")
            print(f"First 300 chars of response: {quiz_text[:300]}")
            
            # Parse the generated quiz
            questions = self._parse_quiz_response(quiz_text)
            print(f"Parsed {len(questions)} questions from response")
            
            # If parsing failed, try a backup structured approach
            if len(questions) == 0:
                print("Primary parsing failed, trying backup approach...")
                questions = self._backup_parse_quiz(quiz_text, num_questions)
                print(f"Backup parsing found {len(questions)} questions")
            
            return {
                "questions": questions,
                "metadata": {
                    "difficulty": difficulty,
                    "topic": topic,
                    "question_count": len(questions)
                }
            }
        except Exception as e:
            import traceback
            print(f"Error generating quiz: {e}")
            traceback.print_exc()
            return {"questions": [], "metadata": {}, "error": str(e)}
    
    def _build_quiz_prompt(self, context: str, num_questions: int, difficulty: str, topic: str = None) -> str:
        """Build the prompt for quiz generation"""
        # Cap context length to avoid token issues
        max_context_length = 4000
        if len(context) > max_context_length:
            context = context[:max_context_length] + "... [truncated for length]"
        
        topic_instruction = f"focusing on {topic}" if topic else "covering key concepts"
        
        # Create a very explicit, structured prompt that forces the correct format
        prompt = f"""Generate a multiple-choice quiz based on the educational content below.

IMPORTANT: Follow this EXACT format for each question:
Q1: [Question text]
A. [Option 1]
B. [Option 2]
C. [Option 3]
D. [Option 4]
Correct Answer: [Just the letter of the correct answer - A, B, C, or D]
Explanation: [Brief explanation of why the answer is correct]

REQUIREMENTS:
- Create exactly {num_questions} multiple-choice questions {topic_instruction}
- Difficulty level: {difficulty}
- Each question must have exactly 4 options (A, B, C, D)
- Only one option should be correct
- The correct answer must be indicated with ONLY the letter (A, B, C, or D)
- Each question must follow the format above EXACTLY

EDUCATIONAL CONTENT:
{context}

Remember to follow the exact format specified above. Each question should have:
1. A question number and text
2. Four answer options labeled A through D
3. The correct answer indicated with just the letter
4. A brief explanation
"""
        return prompt
    
    def _parse_quiz_response(self, quiz_text: str) -> List[Dict[str, Any]]:
        """Parse the generated quiz text into structured questions"""
        questions = []
        
        # First, determine if we have any questions at all
        if not ("Q1:" in quiz_text or "Q1." in quiz_text or "Question 1:" in quiz_text):
            print("No questions found in quiz text using primary format detection")
            return questions
            
        # Normalize question format
        quiz_text = quiz_text.replace("Q1.", "Q1:").replace("Q2.", "Q2:").replace("Q3.", "Q3:")
        quiz_text = quiz_text.replace("Q4.", "Q4:").replace("Q5.", "Q5:").replace("Q6.", "Q6:")
        quiz_text = quiz_text.replace("Question 1:", "Q1:").replace("Question 2:", "Q2:").replace("Question 3:", "Q3:")
        
        # Pattern to identify questions
        question_pattern = r"Q(\d+):\s*(.*?)(?=\nA\.|\nA\s|$)"
        
        # Find all questions
        question_matches = re.finditer(question_pattern, quiz_text, re.DOTALL)
        
        for q_match in question_matches:
            q_number = q_match.group(1)
            q_text = q_match.group(2).strip()
            
            # Extract the full question block
            question_start_pos = q_match.start()
            next_q_pattern = r"\nQ" + str(int(q_number) + 1) + ":"
            next_q_match = re.search(next_q_pattern, quiz_text[question_start_pos:])
            if next_q_match:
                question_end_pos = question_start_pos + next_q_match.start()
                question_block = quiz_text[question_start_pos:question_end_pos]
            else:
                question_block = quiz_text[question_start_pos:]
            
            # Find options, answer and explanation
            options_pattern = r"([A-D])\.?\s*(.*?)(?=\n[A-D]\.|\n[A-D]\s|Correct Answer:|$)"
            
            # Try different answer patterns
            answer_patterns = [
                r"Correct Answer:\s*([A-D])",
                r"Correct Answer:\s*([A-D])\.?",
                r"Answer:\s*([A-D])",
                r"Answer: ([A-D])\.",
                r"The correct answer is ([A-D])",
                r"Correct: ([A-D])"
            ]
            
            explanation_pattern = r"(?:Explanation|Explanation:|Why):\s*(.*?)(?=\nQ\d+:|$)"
            
            # Find options
            options = {}
            for opt_match in re.finditer(options_pattern, question_block, re.DOTALL):
                opt_letter = opt_match.group(1)
                opt_text = opt_match.group(2).strip()
                options[opt_letter] = opt_text
            
            # Find correct answer using multiple patterns
            correct_answer = None
            for pattern in answer_patterns:
                answer_match = re.search(pattern, question_block)
                if answer_match:
                    correct_answer = answer_match.group(1)
                    break
            
            # Find explanation
            explanation_match = re.search(explanation_pattern, question_block, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else ""
            
            # If we can't find the explanation with the pattern, try to infer it
            if not explanation and correct_answer:
                # Try to find any text after "Correct Answer: X" until the next question
                explanation_pattern_alt = r"Correct Answer:.*?([A-D]).*?\n(.*?)(?=\nQ\d+:|$)"
                explanation_match_alt = re.search(explanation_pattern_alt, question_block, re.DOTALL)
                if explanation_match_alt:
                    explanation = explanation_match_alt.group(2).strip()
            
            # Debug the question parsing
            print(f"Parsed Q{q_number}: options={len(options)}, answer={correct_answer}, explanation_length={len(explanation)}")
            
            # Add question to list if we have all required components
            if len(options) > 0 and correct_answer:
                questions.append({
                    "id": f"q{q_number}",
                    "text": q_text,
                    "options": options,
                    "correct_answer": correct_answer,
                    "explanation": explanation if explanation else "No explanation provided."
                })
        
        return questions
    
    def _backup_parse_quiz(self, quiz_text: str, num_questions: int) -> List[Dict[str, Any]]:
        """Backup approach to parse quiz when standard parsing fails"""
        questions = []
        
        # Split by blank lines or question numbers
        chunks = re.split(r'\n\s*\n|\n(?=Q\d+:|\d+\.)', quiz_text)
        
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
                
            # Skip if this doesn't look like a question
            if not any(x in chunk.lower() for x in ['?', 'a.', 'b.', 'c.', 'd.']):
                continue
                
            # Extract question text - anything before the first option
            question_text = ""
            options_text = chunk
            
            # Try to find the question text
            q_match = re.search(r'(?:Q\d+:|^\d+\.|Question \d+:)?\s*(.*?)(?=\nA\.|\n\(A\)|\nA\s)', chunk, re.DOTALL)
            if q_match:
                question_text = q_match.group(1).strip()
                options_text = chunk[q_match.end():]
            else:
                # Fallback - just get everything before the first option
                parts = re.split(r'\n(?=A\.|\(A\)|A\s)', chunk, 1)
                if len(parts) > 1:
                    question_text = parts[0].strip()
                    options_text = parts[1]
                else:
                    question_text = f"Question {i+1}"
            
            # Find all options
            options = {}
            for letter in ['A', 'B', 'C', 'D']:
                opt_pattern = r'(?:' + letter + r'\.|' + letter + r'\s|\(' + letter + r'\))\s*(.*?)(?=\n[A-D]\.|\n\([A-D]\)|\n[A-D]\s|Correct|Answer|correct|$)'
                opt_match = re.search(opt_pattern, options_text, re.DOTALL)
                if opt_match:
                    options[letter] = opt_match.group(1).strip()
            
            # Try to find correct answer
            correct_answer = None
            for pattern in [
                r'(?:Correct Answer|Answer|correct)(?::|\sis)?\s*([A-D])',
                r'The answer is ([A-D])'
            ]:
                answer_match = re.search(pattern, chunk)
                if answer_match:
                    correct_answer = answer_match.group(1)
                    break
            
            # If still no answer, try to infer by looking for clues
            if not correct_answer and "correct" in chunk.lower():
                for letter in ['A', 'B', 'C', 'D']:
                    if f"option {letter} is correct" in chunk.lower() or f"{letter} is correct" in chunk.lower():
                        correct_answer = letter
                        break
            
            # If still no answer, select 'A' as default (better than nothing)
            if not correct_answer and options.get('A'):
                correct_answer = 'A'
                print(f"Warning: No correct answer found for question {i+1}, defaulting to A")
            
            # Add to questions if we have enough info
            if question_text and len(options) >= 2 and correct_answer:
                questions.append({
                    "id": f"q{i+1}",
                    "text": question_text,
                    "options": options,
                    "correct_answer": correct_answer,
                    "explanation": "Explanation not available in this quiz format."
                })
        
        return questions