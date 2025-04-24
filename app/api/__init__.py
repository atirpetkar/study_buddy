from fastapi import APIRouter
from app.api import user, vectorstore, chat

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(vectorstore.router, prefix="/vectorstore", tags=["vectorstore"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])