from fastapi import APIRouter, HTTPException, status
from supabase import create_async_client
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from app.api.deps import CurrentUser, SessionDep
from app.schemas.user_profile import (
    UpdateEmailIn,
    UpdatePasswordIn,
    UserProfilePublic,
    UserProfileUpdate,
)
from app.services.user_profile_service import (
    update_user_profile,
)
from app.models.user_profile import UserProfile
from app.utils.global_variables import RESERVED
from app.core.config import settings


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


# Authenticated: update my login email
@router.patch("/me/email")
async def update_my_email(body: UpdateEmailIn, user: CurrentUser):
    """
    Change the auth email for the current user.
    Supabase may require email confirmation depending on your project settings.
    """
    sb = await create_async_client(settings.SUPABASE_URL, settings.SUPABASE_KEY_ANON)
    # Act as the user (respecting all auth rules)
    sb.auth.set_session(user.access_token, user.refresh_token)

    # 1) Re-auth with current password to prove possession
    try:
        auth_check = await sb.auth.sign_in_with_password(
            {"email": user.email, "password": body.password}
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    if not auth_check or not auth_check.user:
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    try:
        await sb.auth.update_user({"email": body.new_email})
    except Exception as e:
        # Typical causes: email already in use, invalid format, rate limits
        raise HTTPException(status_code=400, detail=str(e) or "Failed to update email")

    return {
        "message": "If required, a confirmation email has been sent. Your email will update once confirmed.",
        "user_id": str(user.id),
        "pending_new_email": body.new_email,
    }


# Authenticated: update my password
@router.patch("/me/password")
async def update_my_password(body: UpdatePasswordIn, user: CurrentUser):
    """
    Update the user's password. We re-authenticate with the current password
    before applying the change.
    """
    sb = await create_async_client(settings.SUPABASE_URL, settings.SUPABASE_KEY_ANON)

    # 1) Re-auth with current password to prove possession
    try:
        auth_check = await sb.auth.sign_in_with_password(
            {"email": user.email, "password": body.current_password}
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    if not auth_check or not auth_check.user:
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    # 2) Now act as the user (use their token) and change the password
    sb.auth.set_session(user.access_token, None)
    try:
        await sb.auth.update_user({"password": body.new_password})
    except Exception as e:
        # e.g., password policy violations
        raise HTTPException(
            status_code=400, detail=str(e) or "Failed to update password"
        )

    # Depending on your Supabase settings, existing sessions may be invalidated.
    # Prompt the client to log in again.
    return {
        "message": "Password updated. You may need to log in again on other devices.",
        "user_id": str(user.id),
    }


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
