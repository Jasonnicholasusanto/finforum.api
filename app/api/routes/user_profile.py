from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import CurrentUser, SessionDep
from app.schemas.user_profile import (
    UserProfileRead,
    UserProfileUpdate,
)
from app.services.user_profile_service import (
    get_user_profile,
    update_user_profile,
)

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/{user_id}", response_model=UserProfileRead)
def read_profile(user: CurrentUser, db: Session = Depends(SessionDep)):
    profile = get_user_profile(db, user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/{user_id}", response_model=UserProfileRead)
def update_profile(
    user: CurrentUser, update: UserProfileUpdate, db: Session = Depends(SessionDep)
):
    profile = update_user_profile(db, user.id, update)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
