# app/utils/error_handler.py
import traceback
import logging
from typing import Dict, Any, Callable, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StudyBuddyError(Exception):
    """Base exception class for Study Buddy errors"""
    def __init__(self, message: str, error_code: str = "unknown_error", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class DocumentProcessingError(StudyBuddyError):
    """Error during document processing"""
    def __init__(self, message: str):
        super().__init__(message, "document_processing_error", 400)

class VectorStoreError(StudyBuddyError):
    """Error with vector store operations"""
    def __init__(self, message: str):
        super().__init__(message, "vector_store_error", 500)

class ModelInferenceError(StudyBuddyError):
    """Error during model inference/generation"""
    def __init__(self, message: str):
        super().__init__(message, "model_inference_error", 500)

class ContentGenerationError(StudyBuddyError):
    """Error during content generation (quiz, flashcards, etc.)"""
    def __init__(self, message: str):
        super().__init__(message, "content_generation_error", 500)

class DatabaseError(StudyBuddyError):
    """Error with database operations"""
    def __init__(self, message: str):
        super().__init__(message, "database_error", 500)

# Error handler for FastAPI
async def study_buddy_exception_handler(request: Request, exc: StudyBuddyError):
    """Handle Study Buddy specific exceptions"""
    logger.error(f"StudyBuddyError: {exc.error_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": exc.error_code,
            "message": exc.message,
            "path": request.url.path
        }
    )

# Function to capture and handle errors in async functions
async def safe_execute(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Execute a function safely and handle exceptions
    
    Args:
        func: Function to execute
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Dictionary with success flag and result or error information
    """
    try:
        result = await func(*args, **kwargs)
        return {
            "success": True,
            "result": result
        }
    except StudyBuddyError as e:
        logger.error(f"Caught StudyBuddyError: {e.error_code} - {e.message}")
        return {
            "success": False,
            "error_code": e.error_code,
            "message": e.message
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error_code": "unexpected_error",
            "message": str(e)
        }

# Function to register error handlers with FastAPI app
def register_error_handlers(app):
    """Register all error handlers with the FastAPI app"""
    
    @app.exception_handler(StudyBuddyError)
    async def handle_study_buddy_error(request, exc):
        return await study_buddy_exception_handler(request, exc)
    
    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request, exc):
        return await http_exception_handler(request, exc)
    
    @app.exception_handler(Exception)
    async def handle_general_exception(request, exc):
        logger.error(f"Uncaught exception: {str(exc)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "error_code": "server_error",
                "message": "An unexpected error occurred",
                "path": request.url.path
            }
        )