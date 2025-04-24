# app/utils/context_retrieval.py
import numpy as np
from typing import Dict, Any, List, Set

async def retrieve_enhanced_context(vector_client, query: str, top_k: int = 5, threshold: float = 0.9) -> Dict[str, Any]:
    """Enhanced context retrieval with better filtering and ranking"""
    try:
        # Skip if no vector client available
        if not vector_client:
            return {"results": [], "sources": []}
            
        # Generate embedding for query
        query_embedding = await vector_client.generate_embedding(query)
        query_np = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        
        if vector_client.index.ntotal == 0:
            print("Retrieval failed: Index is empty")
            return {"results": [], "sources": []}
            
        # Retrieve more candidates than needed, will filter later
        k = min(top_k * 2, vector_client.index.ntotal)
        D, I = vector_client.index.search(query_np, k)
        
        # Process results with filtering
        hits = []
        sources = set()
        
        for idx, dist in zip(I[0], D[0]):
            # Skip invalid results
            if idx == -1 or idx >= len(vector_client.metadata):
                continue
                
            # Apply distance threshold
            if dist > threshold:
                continue
                
            meta = vector_client.metadata[idx]
            
            # Add source to tracking
            source = meta.get("filename", "unknown")
            sources.add(source)
            
            # Add to hits
            hits.append({
                "content": meta["chunk"],
                "metadata": {
                    "source": source,
                    "chunk_index": meta.get("chunk_index", 0),
                    "upload_time": meta.get("upload_time", ""),
                },
                "distance": float(dist)
            })
            
            # Stop if we have enough results
            if len(hits) >= top_k:
                break
        
        print(f"Enhanced retrieval found {len(hits)} relevant chunks from {len(sources)} sources")
        return {
            "results": hits,
            "sources": list(sources)
        }
    except Exception as e:
        print(f"Error in enhanced retrieval: {e}")
        return {"results": [], "sources": []}

def format_context_by_source(search_results: Dict[str, Any]) -> tuple:
    """Organize context chunks by their source"""
    if not search_results or not search_results.get("results"):
        return "", []
    
    # Group by source
    sources_dict = {}
    for result in search_results["results"]:
        source = result.get("metadata", {}).get("source", "unknown")
        if source not in sources_dict:
            sources_dict[source] = []
        sources_dict[source].append(result["content"])
    
    # Format context by source
    formatted_contexts = []
    for source, contents in sources_dict.items():
        source_context = f"From {source}:\n" + "\n".join(contents)
        formatted_contexts.append(source_context)
    
    context = "\n\n".join(formatted_contexts)
    context_sources = list(sources_dict.keys())
    
    return context, context_sources
