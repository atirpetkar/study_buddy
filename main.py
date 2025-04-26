# main.py: FastAPI entry point
# from fastapi import FastAPI
# from app.api import api_router

# app = FastAPI()

# # Include all routers from api_router
# app.include_router(api_router)


# main.py: FastAPI entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers from api_router
app.include_router(api_router)
