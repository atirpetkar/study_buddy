from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import os
import io
import datetime
import chromadb
from chromadb.utils import embedding_functions
import pdfplumber
from chromadb.config import Settings

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

# ChromaDB client setup with DuckDB backend
chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb", persist_directory="./db/chroma_duckdb"))
collection = chroma_client.get_or_create_collection("file_chunks")

@router.post("/vectorize/upload")
async def upload_and_vectorize(files: List[UploadFile] = File(...)):
    all_metadatas = []
    for file in files:
        text = await extract_text(file)
        chunks = chunk_text(text)
        now = datetime.datetime.utcnow().isoformat()
        metadatas = []
        for idx, chunk in enumerate(chunks):
            metadata = {
                "filename": file.filename,
                "filetype": os.path.splitext(file.filename)[1][1:],
                "chunk_index": idx,
                "upload_time": now
            }
            # Store in ChromaDB
            collection.add(
                documents=[chunk],
                metadatas=[metadata],
                ids=[f"{file.filename}-{idx}-{now}"]
            )
            metadatas.append(metadata)
        all_metadatas.append({"file": file.filename, "chunks": len(chunks), "metadatas": metadatas})
    return JSONResponse(content={"status": "success", "files": all_metadatas})
