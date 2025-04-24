# main.py: FastAPI entry point
from fastapi import FastAPI
from app.api import api_router

app = FastAPI()

# Include all routers from api_router
app.include_router(api_router)
