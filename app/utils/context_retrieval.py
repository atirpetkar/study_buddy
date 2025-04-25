# app/utils/context_retrieval.py
import numpy as np
from typing import Dict, Any, List, Set

# Update in app/utils/context_retrieval.py
async def retrieve_enhanced_context(vector_client, query: str, top_k: int = 5, threshold: float = 1.5):
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
                
            # Apply distance threshold - INCREASED from 0.9 to 1.5 to be more permissive
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

# Add to app/utils/context_retrieval.py
async def retrieve_topic_context(vector_client, topic: str, min_chunks: int = 8, max_chunks: int = 15):
    """Retrieve a larger context about a specific topic for quiz generation"""
    try:
        # Generate an expanded query to find more relevant content
        expanded_query = f"{topic} key concepts important definitions examples"
        
        # Get more chunks than usual
        search_results = await retrieve_enhanced_context(
            vector_client, 
            expanded_query, 
            top_k=max_chunks, 
            threshold=2.0  # More permissive threshold
        )
        
        # Sort chunks by source and chunk_index to preserve document ordering
        chunks = []
        if search_results.get("results"):
            chunks = sorted(
                search_results["results"],
                key=lambda x: (
                    x["metadata"]["source"], 
                    x["metadata"].get("chunk_index", 0)
                )
            )
        
        # Group chunks by source
        source_chunks = {}
        for chunk in chunks:
            source = chunk["metadata"]["source"]
            if source not in source_chunks:
                source_chunks[source] = []
            source_chunks[source].append(chunk)
        
        # Build a coherent context from the chunks
        context_sections = []
        sources = []
        
        for source, source_list in source_chunks.items():
            # Sort by chunk index to maintain order
            source_list.sort(key=lambda x: x["metadata"].get("chunk_index", 0))
            
            # Take a continuous section from each source
            content = "\n".join([c["content"] for c in source_list])
            
            # Only add non-empty content
            if content.strip():
                context_sections.append(f"From {source}:\n{content}")
                sources.append(source)
        
        # Combine everything into a single context
        full_context = "\n\n".join(context_sections)
        
        # Make sure we have enough content
        if not full_context or len(full_context.split()) < 100:
            print(f"Warning: Retrieved context about '{topic}' is too small ({len(full_context.split()) if full_context else 0} words)")
            return {"context": "", "sources": []}
        
        print(f"Retrieved {len(context_sections)} context sections with total {len(full_context.split())} words")
        return {"context": full_context, "sources": sources}
    except Exception as e:
        print(f"Error retrieving topic context: {e}")
        return {"context": "", "sources": []}