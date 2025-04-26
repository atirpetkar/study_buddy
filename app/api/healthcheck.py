from datetime import datetime
from fastapi import APIRouter
# Add this to your FastAPI app, likely in your main.py file after the app definition
# or in one of your router files
router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "Study Buddy API is running",
        "timestamp": datetime.now().isoformat()
    }