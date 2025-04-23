# main.py: FastAPI entry point
from fastapi import FastAPI
from app.api import user
from app.api import vector_store

app = FastAPI()

# Include user router
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(vector_store.router, prefix="/vectorize", tags=["vectorstore"])
