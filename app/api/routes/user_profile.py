from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from app.api.deps import CurrentUser, SessionDep
from app.schemas.user_profile import UserProfilePublic, UserProfileUpdate
from app.services.user_profile_service import (
    update_user_profile,
)
from app.models.user_profile import UserProfile
from app.utils.global_variables import RESERVED

router = APIRouter(prefix="/users", tags=["profiles"])


# Authenticated: Get my a logged in user's profile
@router.get("/me", response_model=UserProfilePublic)
def get_my_profile(user: CurrentUser, db: SessionDep):
    prof = db.get(UserProfile, user.id)
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )
    return UserProfilePublic.model_validate(prof, from_attributes=True)


# Authenticated: Update a logged in user's profile
@router.patch("/me", response_model=UserProfilePublic)
def patch_my_profile(
    update: UserProfileUpdate,
    user: CurrentUser,
    db: SessionDep,
):
    """
    Partially update the authenticated user's profile.
    Only fields provided in the body will be updated.
    """

    # block changing to a reserved username
    if update.username and update.username.lower() in RESERVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username is reserved"
        )

    try:
        prof = update_user_profile(db, user_id=user.id, profile_update=update)
    except IntegrityError as e:
        # Likely UNIQUE violation on username or phone_number
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or phone number already in use",
        ) from e

    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    # Build the private view; include auth email if your schema has it
    me = UserProfilePublic.model_validate(prof, from_attributes=True)
    if hasattr(me, "email"):  # optional: if your private schema includes email
        me.email = user.email
    return me


# Public: Get a profile by username
@router.get("/@{username}", response_model=UserProfilePublic)
async def get_profile_by_username(
    username: str, db: SessionDep
) -> UserProfilePublic | None:
    # If you use citext for username, this lookup is case-insensitive automatically.
    if username.lower() in RESERVED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    profile = db.exec(
        select(UserProfile).where(UserProfile.username == username)
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserProfilePublic.model_validate(profile, from_attributes=True)
