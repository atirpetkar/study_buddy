# app/api/vectorstore.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import os
import io
import datetime
import pdfplumber
import numpy as np

from app.core.vector_store import get_vector_store_client
import faiss
import pickle

router = APIRouter()

# Helper: extract text from txt or pdf
async def extract_text(file: UploadFile) -> str:
    if file.filename.lower().endswith('.txt'):
        content = await file.read()
        return content.decode('utf-8')
    elif file.filename.lower().endswith('.pdf'):
        content = await file.read()
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or '' for page in pdf.pages)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

# Helper: chunk text (simple N char chunks)
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

@router.post("/upload")
async def upload_and_vectorize(files: List[UploadFile] = File(...)):
    # Get client
    vector_client = get_vector_store_client()
    
    # Reset the index to ensure dimensions match
    vector_client.index = faiss.IndexFlatL2(vector_client.embedding_dim)
    vector_client.metadata = []
    
    all_metadatas = []
    for file in files:
        text = await extract_text(file)
        chunks = chunk_text(text)
        now = datetime.datetime.utcnow().isoformat()
        metadatas = []
        
        print(f"Processing {file.filename} with {len(chunks)} chunks")
        
        # Process each chunk
        for idx, chunk in enumerate(chunks):
            try:
                print(f"Processing chunk {idx} from {file.filename}...")
                
                # Generate embedding
                embedding = await vector_client.generate_embedding(chunk)
                
                # Create metadata
                metadata = {
                    "filename": file.filename,
                    "filetype": os.path.splitext(file.filename)[1][1:] if '.' in file.filename else '',
                    "chunk_index": idx,
                    "upload_time": now,
                    "chunk": chunk
                }
                
                # Add to FAISS index
                emb_np = np.array(embedding, dtype=np.float32).reshape(1, -1)
                vector_client.index.add(emb_np)
                vector_client.metadata.append(metadata)
                metadatas.append(metadata)
                
                print(f"Successfully processed chunk {idx}")
            except Exception as e:
                print(f"Error processing chunk {idx}: {str(e)}")
                # Continue with other chunks instead of stopping
        
        all_metadatas.append({"file": file.filename, "chunks": len(metadatas), "metadatas": metadatas})
    
    # Save index and metadata
    os.makedirs(os.path.dirname(vector_client.index_path), exist_ok=True)
    try:
        faiss.write_index(vector_client.index, vector_client.index_path)
        with open(vector_client.meta_path, "wb") as f:
            pickle.dump(vector_client.metadata, f)
        
        print(f"Vector store now has {vector_client.index.ntotal} vectors and {len(vector_client.metadata)} metadata entries")
    except Exception as e:
        print(f"Error saving index: {str(e)}")
        return JSONResponse(content={"status": "error", "message": f"Error saving index: {str(e)}"}, status_code=500)
    
    return JSONResponse(content={"status": "success", "files": all_metadatas})

@router.post("/search")
async def semantic_search(query: str, top_k: int = 5):
    vector_client = get_vector_store_client()
    return await vector_client.search(query, top_k)

@router.post("/reset")
async def reset_vector_store():
    vector_client = get_vector_store_client()
    vector_client.index = faiss.IndexFlatL2(vector_client.embedding_dim)
    vector_client.metadata = []
    
    # Remove files if they exist
    if os.path.exists(vector_client.index_path):
        os.remove(vector_client.index_path)
    if os.path.exists(vector_client.meta_path):
        os.remove(vector_client.meta_path)
    
    return {"status": "reset successful"}