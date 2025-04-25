# Add to app/core/content_analyzer.py (new file)
from typing import List, Dict, Any

class ContentAnalyzer:
    """Analyzes document content to extract topics and key concepts"""
    
    async def extract_topics(self, content: str, client, model_name: str) -> List[str]:
        """Extract main topics from content"""
        prompt = f"""
        Analyze the following educational content and identify 5-7 main topics covered.
        Return ONLY a comma-separated list of these topics.
        
        CONTENT:
        {content[:4000]}  # Use first 4000 chars to avoid token limits
        
        RESPONSE FORMAT:
        Topic 1, Topic 2, Topic 3, Topic 4, Topic 5
        """
        
        messages = [
            {"role": "system", "content": "You extract key topics from educational content."},
            {"role": "user", "content": prompt}
        ]
        
        response = await client.chat.completions.create(
            messages=messages,
            temperature=0.3,
            max_tokens=100,
            model=model_name
        )
        
        topics_text = response.choices[0].message.content
        topics = [topic.strip() for topic in topics_text.split(',')]
        return topics