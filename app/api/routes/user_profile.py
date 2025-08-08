from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_session
from app.schemas.user_profile import (
    UserProfileCreate,
    UserProfileRead,
    UserProfileUpdate,
)
from app.services.user_profile import (
    create_user_profile,
    get_user_profile,
    update_user_profile,
)
from uuid import UUID

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/{user_id}", response_model=UserProfileRead)
def read_profile(user_id: UUID, db: Session = Depends(get_session)):
    profile = get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/", response_model=UserProfileRead)
def create_profile(profile: UserProfileCreate, db: Session = Depends(get_session)):
    return create_user_profile(db, profile)


@router.put("/{user_id}", response_model=UserProfileRead)
def update_profile(
    user_id: UUID, update: UserProfileUpdate, db: Session = Depends(get_session)
):
    profile = update_user_profile(db, user_id, update)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
