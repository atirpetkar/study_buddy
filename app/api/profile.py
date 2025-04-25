# app/api/profile.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
import datetime
import json

from app.models import db, repository
from app.schemas.profile import ProfileCreateRequest, ProfileUpdateRequest, ProfileResponse

router = APIRouter()

@router.post("/create", response_model=ProfileResponse)
async def create_profile(request: ProfileCreateRequest, db_session = Depends(db.get_db)):
    """Create a new student profile"""
    try:
        # Check if profile already exists
        existing_profile = repository.get_user_profile(db_session, request.user_id)
        if existing_profile:
            raise HTTPException(status_code=400, detail="Profile already exists for this user")
        
        # Create profile
        profile = repository.create_user_profile(
            db_session,
            user_id=request.user_id,
            profile_data=request.dict()
        )
        
        # Format response
        profile_data = repository.get_user_profile(db_session, request.user_id)
        
        return ProfileResponse(
            user_id=request.user_id,
            exam_type=profile_data.get("exam_type"),
            study_preferences=profile_data.get("study_preferences"),
            available_study_time=profile_data.get("available_study_time"),
            goals=profile_data.get("goals"),
            topics=profile_data.get("initial_topics"),
            created_at=profile_data.get("created_at"),
            updated_at=profile_data.get("updated_at")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating profile: {str(e)}")

@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str, db_session = Depends(db.get_db)):
    """Get student profile"""
    try:
        profile = repository.get_user_profile(db_session, user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return ProfileResponse(
            user_id=profile["user_id"],
            exam_type=profile["exam_type"],
            study_preferences=profile["study_preferences"],
            available_study_time=profile["available_study_time"],
            goals=profile["goals"],
            topics=profile["topics"],
            created_at=profile["created_at"],
            updated_at=profile["updated_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")

@router.put("/{user_id}", response_model=ProfileResponse)
async def update_profile(user_id: str, request: ProfileUpdateRequest, db_session = Depends(db.get_db)):
    """Update student profile"""
    try:
        # Check if profile exists
        existing_profile = repository.get_user_profile(db_session, user_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Update profile
        profile_data = request.dict(exclude_unset=True)  # Only include set fields
        updated_profile = repository.update_user_profile(
            db_session,
            user_id=user_id,
            profile_data=profile_data
        )
        
        # Format response
        profile_data = repository.get_user_profile(db_session, user_id)
        
        return ProfileResponse(
            user_id=profile_data["user_id"],
            exam_type=profile_data["exam_type"],
            study_preferences=profile_data["study_preferences"],
            available_study_time=profile_data["available_study_time"],
            goals=profile_data["goals"],
            topics=profile_data["topics"],
            created_at=profile_data["created_at"],
            updated_at=profile_data["updated_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")