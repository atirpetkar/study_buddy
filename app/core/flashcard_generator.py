# app/core/flashcard_generator.py
from typing import List, Dict, Any
import re
import uuid

class FlashcardGenerator:
    """Service for generating flashcards from document content"""
    
    async def generate_flashcards(self, 
                               context: str,
                               num_cards: int = 8,
                               topic: str = None,
                               client=None,
                               model_name: str = None) -> Dict[str, Any]:
        """
        Generate flashcards based on the provided context
        
        Args:
            context: Text from retrieved documents
            num_cards: Number of flashcards to generate
            topic: Optional specific topic to focus on
            client: LLM client
            model_name: LLM model name
            
        Returns:
            Dict containing flashcards and metadata
        """
        if not context or not client:
            print("Missing context or client in generate_flashcards")
            return {"cards": [], "metadata": {}, "error": "Missing context or LLM client"}
        
        # Build prompt for flashcard generation
        prompt = self._build_flashcard_prompt(context, num_cards, topic)
        
        try:
            print(f"Sending prompt to model {model_name} - prompt length: {len(prompt)}")
            
            # Call the LLM to generate flashcards
            messages = [
                {"role": "system", "content": "You are a flashcard generation assistant specialized in creating educational flashcards. Follow the requested format exactly."},
                {"role": "user", "content": prompt}
            ]
            
            response = await client.chat.completions.create(
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                model=model_name
            )
            
            flashcards_text = response.choices[0].message.content
            print(f"Received response - length: {len(flashcards_text)}")
            
            # Parse the generated flashcards
            cards = self._parse_flashcards_response(flashcards_text)
            print(f"Parsed {len(cards)} flashcards from response")
            
            return {
                "cards": cards,
                "metadata": {
                    "topic": topic,
                    "card_count": len(cards)
                }
            }
        except Exception as e:
            import traceback
            print(f"Error generating flashcards: {e}")
            traceback.print_exc()
            return {"cards": [], "metadata": {}, "error": str(e)}
    
    def _build_flashcard_prompt(self, context: str, num_cards: int, topic: str = None) -> str:
        """Build the prompt for flashcard generation"""
        # Cap context length to avoid token issues
        max_context_length = 4000
        if len(context) > max_context_length:
            context = context[:max_context_length] + "... [truncated for length]"
        
        topic_instruction = f"focusing on {topic}" if topic else "covering key concepts"
        
        prompt = f"""Generate {num_cards} flashcards based on the educational content below.

IMPORTANT: Follow this EXACT format for each flashcard:
Card [number]:
Front: [Term, concept, or question]
Back: [Definition, explanation, or answer]

REQUIREMENTS:
- Create exactly {num_cards} flashcards {topic_instruction}
- Front side should contain a term, concept, or question
- Back side should contain a concise but comprehensive definition, explanation, or answer
- Make sure each flashcard covers a unique concept
- Ensure the cards cover the most important concepts from the material
- Use clear, concise language appropriate for studying

EDUCATIONAL CONTENT:
{context}

Remember to follow the exact format specified above. Each flashcard should have:
1. A card number
2. Front content with a term or question
3. Back content with a definition or answer
"""
        return prompt
    
    def _parse_flashcards_response(self, text: str) -> List[Dict[str, Any]]:
        """Parse the generated flashcards text into structured cards"""
        cards = []
        
        # Pattern to identify cards
        card_pattern = r"Card\s+(\d+):\s*\n+Front:\s*(.*?)\s*\n+Back:\s*(.*?)(?=\n+Card\s+\d+:|\Z)"
        
        # Find all cards
        card_matches = re.finditer(card_pattern, text, re.DOTALL)
        
        for match in card_matches:
            card_number = match.group(1)
            front = match.group(2).strip()
            back = match.group(3).strip()
            
            if front and back:
                cards.append({
                    "id": f"card{card_number}",
                    "front": front,
                    "back": back
                })
        
        return cards