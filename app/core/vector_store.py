# app/core/vector_store.py
import faiss
import pickle
import os
import numpy as np
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class VectorStoreClient:
    def __init__(self):
        self.index_path = "./db/faiss.index"
        self.meta_path = "./db/faiss_meta.pkl"
        self.embedding_dim = 3072  # For text-embedding-3-large's dimension
        
        # Configure client
        self.token = os.environ.get("GITHUB_TOKEN")
        self.endpoint = "https://models.inference.ai.azure.com"
        self.model_name = "text-embedding-3-large"
        
        self.client = OpenAI(
            base_url=self.endpoint,
            api_key=self.token,
        )
        
        # Load index and metadata if available
        self._load_index()
    
    def _load_index(self):
        """Load FAISS index and metadata from disk if available"""
        try:
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
            print(f"Loaded vector store with {len(self.metadata)} entries")
        except Exception as e:
            print(f"Vector store not found or error loading: {e}")
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.metadata = []
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text string"""
        try:
            # Make sure text is not empty
            if not text or not text.strip():
                raise ValueError("Cannot generate embedding for empty text")
                
            # Truncate very long texts
            max_tokens = 8000  # Approximate token limit for embedding model
            if len(text) > max_tokens * 4:  # Rough approximation of characters per token
                print(f"Text too long ({len(text)} chars), truncating...")
                text = text[:max_tokens * 4]
            
            # Create a synchronous call in an async context
            response = self.client.embeddings.create(
                input=[text],
                model=self.model_name
            )
            
            print(f"Generated embedding of length: {len(response.data[0].embedding)}")
            
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    async def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search the vector store for relevant content"""
        try:
            # Generate embedding for query
            query_embedding = await self.generate_embedding(query)
            query_np = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
            
            # Check if index is empty
            if self.index.ntotal == 0:
                print("Search failed: Index is empty")
                return {"results": []}
                
            # Search FAISS index
            D, I = self.index.search(query_np, min(top_k * 2, self.index.ntotal))
            
            # Process search results
            hits = []
            seen_content = set()  # Track seen content to avoid duplicates
            
            print(f"Search returned {len(I[0])} results")
            
            for idx, dist in zip(I[0], D[0]):
                # Skip invalid indices
                if idx == -1 or idx >= len(self.metadata):
                    continue
                    
                # Skip results with extreme distances
                if dist > 2.0:
                    continue
                
                meta = self.metadata[idx]
                content = meta["chunk"]
                
                # Skip duplicate content
                content_hash = hash(content)
                if content_hash in seen_content:
                    continue
                    
                seen_content.add(content_hash)
                
                hits.append({
                    "content": content,
                    "metadata": {
                        "source": meta["filename"],
                        "chunk_index": meta["chunk_index"],
                        "upload_time": meta["upload_time"]
                    },
                    "distance": float(dist)
                })
                
                # Stop once we have enough results
                if len(hits) >= top_k:
                    break
            
            print(f"After filtering, returning {len(hits)} results")
            return {"results": hits}
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return {"results": [], "error": str(e)}

# Singleton instance
_vector_store_client = None

def get_vector_store_client() -> VectorStoreClient:
    """Returns a singleton instance of the vector store client"""
    global _vector_store_client
    if _vector_store_client is None:
        _vector_store_client = VectorStoreClient()
    return _vector_store_client