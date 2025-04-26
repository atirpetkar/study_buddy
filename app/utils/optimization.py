# app/utils/optimization.py
import time
import functools
import logging
from typing import Dict, Any, List, Callable, Optional
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def timing_decorator(func):
    """Decorator to measure and log function execution time"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.info(f"Function {func.__name__} executed in {execution_time:.2f} seconds")
        return result
    return wrapper

class EmbeddingCache:
    """Simple cache for document embeddings to avoid regeneration"""
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        
    def get(self, text_hash: str) -> Optional[List[float]]:
        """Get embedding from cache if it exists"""
        result = self.cache.get(text_hash)
        if result is not None:
            self.hits += 1
        else:
            self.misses += 1
        return result
    
    def set(self, text_hash: str, embedding: List[float]) -> None:
        """Add embedding to cache"""
        # Simple LRU: remove random item if cache is full
        if len(self.cache) >= self.max_size:
            # Remove a random key
            key_to_remove = list(self.cache.keys())[0]
            del self.cache[key_to_remove]
        
        self.cache[text_hash] = embedding
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate
        }

class ResultsDeduplicator:
    """Utility to deduplicate search results based on content similarity"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
    
    def deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate results based on content similarity
        
        Args:
            results: List of result dictionaries with "content" key
            
        Returns:
            Deduplicated list of results
        """
        if not results:
            return []
            
        unique_results = []
        seen_contents = []
        
        for result in results:
            content = result.get("content", "")
            is_duplicate = False
            
            # Check if this content is similar to any we've seen
            for seen in seen_contents:
                similarity = self._text_similarity(content, seen)
                if similarity > self.similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_results.append(result)
                seen_contents.append(content)
                
        return unique_results
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity based on word overlap
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        # Convert to sets of words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0
            
        return len(intersection) / len(union)

class ResponseTimeMonitor:
    """Utility to monitor and report component response times"""
    
    def __init__(self):
        self.timings = {}
        
    def start_timer(self, component_name: str) -> int:
        """Start timer for a component"""
        timer_id = int(time.time() * 1000)  # millisecond timestamp
        self.timings[timer_id] = {
            "component": component_name,
            "start_time": time.time(),
            "end_time": None,
            "duration": None
        }
        return timer_id
    
    def end_timer(self, timer_id: int) -> float:
        """End timer and return duration"""
        if timer_id not in self.timings:
            return 0
            
        end_time = time.time()
        self.timings[timer_id]["end_time"] = end_time
        duration = end_time - self.timings[timer_id]["start_time"]
        self.timings[timer_id]["duration"] = duration
        
        return duration
    
    def get_stats(self) -> Dict[str, Any]:
        """Get timing statistics by component"""
        component_stats = {}
        
        for timer_data in self.timings.values():
            component = timer_data["component"]
            duration = timer_data.get("duration")
            
            if duration is None:
                continue
                
            if component not in component_stats:
                component_stats[component] = {
                    "count": 0,
                    "total_time": 0,
                    "min_time": float("inf"),
                    "max_time": 0
                }
                
            stats = component_stats[component]
            stats["count"] += 1
            stats["total_time"] += duration
            stats["min_time"] = min(stats["min_time"], duration)
            stats["max_time"] = max(stats["max_time"], duration)
            stats["avg_time"] = stats["total_time"] / stats["count"]
            
        return component_stats
    
    def get_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        stats = self.get_stats()
        components = []
        
        for component, data in stats.items():
            components.append({
                "component": component,
                "avg_time": data["avg_time"],
                "max_time": data["max_time"],
                "call_count": data["count"]
            })
            
        # Sort by average time (descending)
        components.sort(key=lambda x: x["avg_time"], reverse=True)
        
        return components

# Create singleton instances
embedding_cache = EmbeddingCache()
results_deduplicator = ResultsDeduplicator()
response_time_monitor = ResponseTimeMonitor()