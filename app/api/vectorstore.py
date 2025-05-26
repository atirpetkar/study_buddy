# app/api/vectorstore.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import os
import io
import datetime
import pdfplumber
import numpy as np

from app.core.vector_store import get_vector_store_client
from app.utils.text_preprocessing import clean_text, smart_chunk_text
from app.api.user import get_current_user
# Import database models
from app.models.models import UploadedDocument, DocumentChunk
from app.models.db import get_db
from sqlalchemy.orm import Session
import faiss
import pickle
import re

router = APIRouter()

# Helper: extract text from txt or pdf
async def extract_text(file: UploadFile) -> str:
    """Extract text from txt or pdf files with improved error handling"""
    try:
        file_ext = os.path.splitext(file.filename.lower())[1]
        content = await file.read()
        
        if file_ext == '.txt':
            return content.decode('utf-8')
        elif file_ext == '.pdf':
            text = ""
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ''
                    text += page_text + "\n\n"
            return text
        elif file_ext in ['.md', '.markdown']:
            return content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
    except Exception as e:
        print(f"Error extracting text from {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")

@router.post("/upload")
async def upload_and_vectorize(files: List[UploadFile] = File(...), db: Session = Depends(get_db), user_email: str = "qwe@gmail.com"):
    """
    Upload files, process them into chunks, and add to vector store
    with improved chunking to respect document structure
    """
    # Get client
    vector_client = get_vector_store_client()
    
    all_metadatas = []
    total_chunks = 0
    
    # Don't reset the index - we want to keep all documents in the system
    # Just add the new documents to the existing index
    if vector_client.index is None:
        vector_client.index = faiss.IndexFlatL2(vector_client.embedding_dim)
        vector_client.metadata = []
    
    for file in files:
        try:
            # Extract text from file
            text = await extract_text(file)
            
            # Clean and preprocess the text before chunking
            text = clean_text(text)
            
            # Use improved chunking function, with different approaches for different file types
            if file.filename.lower().endswith(('.md', '.markdown')):
                chunks = smart_chunk_text(text, chunk_size=1200, overlap=150)
            else:
                # For regular text files and PDFs
                chunks = smart_chunk_text(text, chunk_size=1200, overlap=150)
            
            now = datetime.datetime.utcnow()
            now_str = now.isoformat()
            metadatas = []
            
            print(f"Processing {file.filename} with {len(chunks)} chunks")
            
            # Create database entry for the document
            db_document = UploadedDocument(
                file_name=file.filename,
                file_path=f"uploads/{file.filename}",  # This is a placeholder path
                uploaded_at=now,
                # Use email as user_id instead of hardcoded "1"
                user_id=user_email
            )
            db.add(db_document)
            db.flush()  # Get the document ID without committing transaction
            
            print(f"Created document entry with ID: {db_document.id} for user {user_email}")
            
            # Process each chunk
            for idx, chunk in enumerate(chunks):
                try:
                    print(f"Processing chunk {idx} from {file.filename}...")
                    
                    # Generate embedding
                    embedding = await vector_client.generate_embedding(chunk)
                    
                    # Serialize embedding for database storage
                    embedding_str = ','.join([str(x) for x in embedding])
                    
                    # Create database entry for the chunk
                    db_chunk = DocumentChunk(
                        document_id=db_document.id,
                        chunk_text=chunk,
                        embedding=embedding_str,
                        chunk_index=idx
                    )
                    db.add(db_chunk)
                    
                    # Create metadata - now including user_id
                    metadata = {
                        "filename": file.filename,
                        "filetype": os.path.splitext(file.filename)[1][1:] if '.' in file.filename else '',
                        "chunk_index": idx,
                        "upload_time": now_str,
                        "chunk": chunk,
                        "user_id": user_email  # Add user_id to metadata
                    }
                    
                    # Add to FAISS index
                    emb_np = np.array(embedding, dtype=np.float32).reshape(1, -1)
                    vector_client.index.add(emb_np)
                    vector_client.metadata.append(metadata)
                    metadatas.append(metadata)
                    total_chunks += 1
                    
                    print(f"Successfully processed chunk {idx}")
                except Exception as e:
                    print(f"Error processing chunk {idx}: {str(e)}")
                    # Continue with other chunks instead of stopping
            
            all_metadatas.append({
                "file": file.filename, 
                "chunks": len(metadatas), 
                "metadatas": [
                    {
                        "chunk_index": m["chunk_index"],
                        "length": len(m["chunk"])
                    } for m in metadatas
                ]
            })
            
        except Exception as e:
            print(f"Error processing file {file.filename}: {str(e)}")
            return JSONResponse(
                content={"status": "error", "message": f"Error processing {file.filename}: {str(e)}"}, 
                status_code=500
            )
    
    # Save index and metadata
    os.makedirs(os.path.dirname(vector_client.index_path), exist_ok=True)
    try:
        faiss.write_index(vector_client.index, vector_client.index_path)
        with open(vector_client.meta_path, "wb") as f:
            pickle.dump(vector_client.metadata, f)
        
        # Commit database changes
        db.commit()
        
        print(f"Vector store now has {vector_client.index.ntotal} vectors and {len(vector_client.metadata)} metadata entries")
        print(f"Database now has new document entries for user {user_email}")
    except Exception as e:
        db.rollback()  # Rollback transaction on error
        print(f"Error saving index or database entries: {str(e)}")
        return JSONResponse(content={"status": "error", "message": f"Error saving data: {str(e)}"}, status_code=500)
    
    return JSONResponse(content={
        "status": "success", 
        "total_chunks": total_chunks,
        "files": all_metadatas
    })

@router.get("/documents")
async def list_documents(user_email: str = "qwe@gmail.com"):
    """List all documents stored in the vector store for a specific user"""
    vector_client = get_vector_store_client()
    
    if not vector_client.metadata:
        return {"documents": []}
    
    # Process metadata to get a unique list of documents
    document_map = {}
    
    for item in vector_client.metadata:
        # Filter by user_id if present in metadata
        item_user_id = item.get("user_id", None)
        if item_user_id and item_user_id != user_email:
            continue
            
        filename = item["filename"]
        if filename not in document_map:
            document_map[filename] = {
                "filename": filename,
                "filetype": item.get("filetype", ""),
                "upload_time": item.get("upload_time", ""),
                "user_id": item.get("user_id", user_email),
                "chunk_count": 1
            }
        else:
            document_map[filename]["chunk_count"] += 1
    
    # Convert to list and sort by upload time (newest first)
    documents = list(document_map.values())
    documents.sort(key=lambda x: x["upload_time"], reverse=True)
    
    return {
        "document_count": len(documents),
        "total_chunks": sum(doc["chunk_count"] for doc in documents),
        "documents": documents
    }

@router.post("/search")
async def semantic_search(query: str, top_k: int = 5):
    """Search the vector store for relevant content"""
    vector_client = get_vector_store_client()
    return await vector_client.search(query, top_k)

@router.post("/reset")
async def reset_vector_store(db: Session = Depends(get_db)):
    """Reset the vector store and database document records"""
    # Reset vector store
    vector_client = get_vector_store_client()
    vector_client.index = faiss.IndexFlatL2(vector_client.embedding_dim)
    vector_client.metadata = []
    
    # Remove files if they exist
    if os.path.exists(vector_client.index_path):
        os.remove(vector_client.index_path)
    if os.path.exists(vector_client.meta_path):
        os.remove(vector_client.meta_path)
    
    # Clear database tables
    try:
        # Delete document chunks first (child records)
        db.query(DocumentChunk).delete()
        # Then delete documents (parent records)
        db.query(UploadedDocument).delete()
        # Commit changes
        db.commit()
        print("Database document records cleared")
    except Exception as e:
        db.rollback()
        print(f"Error clearing database records: {str(e)}")
        return JSONResponse(
            content={"status": "partial reset", "message": f"Vector store reset but database error: {str(e)}"}, 
            status_code=500
        )
    
    return {"status": "reset successful", "message": "Vector store and database records cleared"}

@router.post("/test-chunking")
async def test_chunking(file: UploadFile = File(...)):
    """Test the chunking algorithm on a file without adding to vector store"""
    try:
        # Extract text
        text = await extract_text(file)
        
        # Clean the text
        text = clean_text(text)
        
        # Chunk the text
        if file.filename.lower().endswith(('.md', '.markdown')):
            chunks = smart_chunk_text(text, chunk_size=1200, overlap=150)
        else:
            # For regular text files and PDFs
            chunks = smart_chunk_text(text, chunk_size=1200, overlap=150)
        
        # Return chunks with stats
        return {
            "filename": file.filename,
            "total_content_length": len(text),
            "chunk_count": len(chunks),
            "chunks": [
                {
                    "index": i,
                    "length": len(chunk),
                    "starts_with": chunk[:100] + "...",
                    "ends_with": "..." + chunk[-100:] if len(chunk) > 100 else chunk
                }
                for i, chunk in enumerate(chunks)
            ]
        }
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": f"Error testing chunking: {str(e)}"}, 
            status_code=500
        )