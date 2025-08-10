from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import CurrentUser, SessionDep
from app.core.auth import get_current_user
from app.schemas.auth import UserIn
from app.schemas.user_profile import (
    UserProfilePublic,
    UserProfileUpdate,
)
from app.services.user_profile_service import (
    get_user_profile,
    update_user_profile,
)

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", response_model=UserProfilePublic)
def read_profile(user: CurrentUser, db: Session = Depends(SessionDep)):
    """
    Get the current authenticated user's profile.
    """
    profile = get_user_profile(db, user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/", response_model=UserProfilePublic)
def update_profile(
    user: CurrentUser,
    update: UserProfileUpdate,
    db: Session = Depends(SessionDep),
):
    """
    Update the current authenticated user's profile.
    """
    profile = update_user_profile(db, user.id, update)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/me")
async def me(current: UserIn = Depends(get_current_user)):
    return {
        "id": current.id,
        "email": current.email,
        "access_token": current.access_token,
    }
