from fastapi import HTTPException, status
from app.api.deps import SessionDep, CurrentUser
from app.services.user_profile_service import get_user_profile_by_auth


def get_current_profile(
    user: CurrentUser,
    db: SessionDep,
):
    profile = get_user_profile_by_auth(db, auth_id=user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )
    return profile
