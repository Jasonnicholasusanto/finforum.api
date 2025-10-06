from uuid import UUID
from fastapi import APIRouter, HTTPException, Response, status

# from supabase import create_async_client
from sqlalchemy.exc import IntegrityError
from app.api.deps import CurrentUser, SessionDep
from app.schemas.user_activity import UserActivityCreate, UserActivityPublic
from app.schemas.user_detail import UserDetailsResponse
from app.schemas.user_profile import (
    UserProfileCreate,
    UserProfileMe,
    UserProfilePublic,
    UserProfileUpdate,
)
from app.services.user_profile_service import (
    _username_exists,
    create_user_profile,
    get_user_profile,
    get_user_profile_by_auth,
    update_user_profile,
)
from app.services.user_activity_service import (
    get_user_activity,
    create_user_activity,
)
from app.services.user_follow_service import (
    get_followers_count,
    get_following_count,
)
from app.utils.global_variables import RESERVED


router = APIRouter(prefix="/me", tags=["me"])


# Authenticated: Get my a logged in user's profile
@router.get("/profile", response_model=UserDetailsResponse)
def get_my_profile(user: CurrentUser, db: SessionDep):
    """
    Return the profile of the currently authenticated user.
    - `user` is injected from JWT (CurrentUser).
    - If no profile exists yet, return 404.
    """
    # auth user id from JWT dependency; handle either .user_id or .id
    auth_user_id = getattr(user, "user_id", None) or getattr(user, "id", None)
    if not auth_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 1) Profile by auth_id (FK to auth.users.id)
    profile = get_user_profile_by_auth(db, auth_id=user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # 2) Activity by user_id (PK)
    activity = get_user_activity(db, profile_id=profile.id)
    if not activity:
        activity = create_user_activity(
            db,
            profile_id=profile.id,
            obj_in=UserActivityCreate(),
        )

    # 3) Followers and Following counts
    followers_count = get_followers_count(db, user_id=profile.id)
    following_count = get_following_count(db, user_id=profile.id)

    return UserDetailsResponse(
        profile=UserProfileMe.model_validate(profile, from_attributes=True),
        activity=UserActivityPublic.model_validate(activity, from_attributes=True)
        if activity
        else None,
        followers_count=followers_count or 0,
        following_count=following_count or 0,
    )


# Authenticated: Create my user profile
@router.post(
    "/profile", response_model=UserProfilePublic, status_code=status.HTTP_201_CREATED
)
def create_my_profile(
    payload: UserProfileCreate,
    user: CurrentUser,
    db: SessionDep,
):
    """
    Create the current user's profile after authentication/onboarding.
    - Derives auth_id and email from the authenticated user.
    - Enforces unique username and email collisions (409).
    - Fails if the profile already exists (409).
    """

    # 1) Guard: reserved usernames
    if payload.username and payload.username.lower() in RESERVED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username is reserved"
        )

    # 2) Prevent duplicate creation for the same auth_id
    if get_user_profile_by_auth(db, auth_id=user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User Profile already exists"
        )

    # 2b) Prevent duplicate username
    exists = _username_exists(session=db, username=payload.username)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
        )

    # 3) Build the create DTO (server never accepts auth_id from client)
    profile_in = UserProfileCreate(**payload.model_dump(exclude_unset=True))
    profile_in.email_address = user.email

    # 4) Create via service
    try:
        profile = create_user_profile(
            db,
            auth_id=UUID(str(user.id)),
            profile_in=profile_in,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username, phone number, or email already in use",
        )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create profile",
        )

    return UserProfilePublic.model_validate(profile, from_attributes=True)


# Authenticated: Update a logged in user's profile
@router.patch("/profile", response_model=UserProfilePublic)
def update_my_profile(
    update: UserProfileUpdate,
    user: CurrentUser,
    db: SessionDep,
):
    """
    Partially update the authenticated user's profile.
    Only fields provided in the request body will be updated.
    """

    # Prevent reserved usernames
    if update.username and update.username.lower() in RESERVED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is reserved",
        )

    # 2b) Prevent duplicate username
    exists = _username_exists(session=db, username=update.username)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
        )

    # 3) Update via service
    try:
        profile = update_user_profile(db, user_id=user.id, profile_update=update)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or phone number already in use",
        )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return UserProfilePublic.model_validate(profile, from_attributes=True)


# Authenticated: Soft delete my profile
@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_my_profile(user: CurrentUser, db: SessionDep):
    profile = get_user_profile(db, user_id=user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    db.soft_delete(db, id=profile.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Authenticated: Reactivate my profile
@router.post("/profile/reactivate", response_model=UserProfilePublic)
def reactivate_my_account(user: CurrentUser, db: SessionDep):
    profile = get_user_profile(db, user_id=user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    profile = db.reactivate(db, id=profile.id)
    return UserProfilePublic.model_validate(profile, from_attributes=True)


# Authenticated: Get my user activity
# @router.get("/activity", response_model=UserActivityPublic)
# async def get_my_activity(user: CurrentUser, db: SessionDep):
#     """
#     Fetch the current user's activity.
#     """
#     activity = db.get(UserActivity, user.id)
#     if not activity:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User activity details not found",
#         )
#     return UserActivityPublic.model_validate(activity, from_attributes=True)
