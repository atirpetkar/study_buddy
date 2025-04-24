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
        self.embedding_dim = 3072  # Updated for text-embedding-3-large's actual dimension
        
        # Configure client exactly as in GitHub example
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
            self.index = faiss.IndexFlatL2(self.embedding_dim)  # Using correct dimension
            self.metadata = []
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text string"""
        try:
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
            
            # Search FAISS index
            if self.index.ntotal == 0:
                print("Search failed: Index is empty")
                return {"results": []}
                
            D, I = self.index.search(query_np, top_k)
            hits = []
            seen = set()
            
            print(f"Search returned {len(I[0])} results")
            
            for idx, dist in zip(I[0], D[0]):
                # Only include valid, unique results
                if idx < len(self.metadata) and idx not in seen and dist < 1e6 and idx != -1:
                    meta = self.metadata[idx]
                    hits.append({
                        "content": meta["chunk"],
                        "metadata": {
                            "source": meta["filename"],
                            "chunk_index": meta["chunk_index"],
                            "upload_time": meta["upload_time"]
                        },
                        "distance": float(dist)
                    })
                    seen.add(idx)
            
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