from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.user_activity import UserActivityPointsBreakdown
from app.schemas.user_detail import UserDetailsPublic
from app.schemas.user_profile import UserProfilePublic, UserProfilesPublic, Username
from app.services.user_activity_service import get_user_points
from app.services.user_profile_service import _username_exists, get_user_profile_by_username, list_user_profiles


router = APIRouter(prefix="/users", tags=["users"])

# Public: Get a profile by username
@router.get("/@{username}", response_model=UserDetailsPublic)
def get_public_user_profile_by_username(username: str, user: CurrentUser, db: SessionDep):
    """
    Public profile lookup by username (case-insensitive).
    Returns 404 if not found or if the profile is deactivated.
    """
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required.")

    profile = get_user_profile_by_username(db, username=username)

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    
    points = get_user_points(db, profile_id=profile.id)

    return UserDetailsPublic(
        profile=UserProfilePublic.model_validate(profile, from_attributes=True),
        points=UserActivityPointsBreakdown.model_validate(points, from_attributes=True)
        if points
        else None,
    )


@router.get("/search", response_model=UserProfilesPublic)
def search_users(
    q: str = Query(..., min_length=1, max_length=64),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: SessionDep = None,
):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required.")
    
    return list_user_profiles(
        db,
        skip=offset,
        limit=limit,
        q=q,
        only_active=True,
    )


@router.get("/check-username")
def check_username(username: Username, db: SessionDep = None):
    """
    Returns {'available': bool}. Case-insensitive check against user_profile.username.
    """
    if not username:
        raise HTTPException(status_code=400, detail="Username is required.")

    exists = _username_exists(session=db, username=username)
    return {"available": not exists}
    