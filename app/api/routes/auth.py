from fastapi import APIRouter, HTTPException, status
from supabase import create_async_client
from app.core.config import settings

from uuid import UUID
from app.schemas.auth import LoginBody, UserSignUp
from app.models.user_profile import UserProfileCreate
from app.schemas.user_profile import UserProfilePublic
from app.services.auth import signup_user
from app.crud.user_profile import user_profile
from app.api.deps import SessionDep
import logging

from app.services.user_profile_service import get_user_profile


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(body: LoginBody, db: SessionDep):
    sb = await create_async_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    res = await sb.auth.sign_in_with_password(
        {"email": body.email, "password": body.password}
    )
    if not res or not res.session or not res.session.access_token:
        # Covers invalid creds, unconfirmed email, etc.
        raise HTTPException(status_code=400, detail="Login failed")

    # Fetch profile by user_id
    uid = UUID(str(res.user.id))
    profile_row = get_user_profile(db, uid)  # returns table model or None

    # Serialize with your public schema (handles from ORM object)
    profile = (
        UserProfilePublic.model_validate(profile_row, from_attributes=True)
        if profile_row
        else None
    )

    return {
        "access_token": res.session.access_token,
        "refresh_token": res.session.refresh_token,
        "token_type": "bearer",
        "user": res.user.model_dump() if res.user else None,
        "profile": profile,
    }


@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def sign_up(user_in: UserSignUp, db: SessionDep):
    try:
        # 1. Create user in Supabase auth (email + password)
        user = await signup_user(user_in.email, user_in.password)
        user_id = user.id

        # 2. Prepare UserProfileCreate object using user_id and other profile data
        profile_data = UserProfileCreate(
            user_id=user_id,
            username=user_in.username or "",
            full_name=user_in.full_name or "",
            phone_number=user_in.phone_number,
            bio=user_in.bio,
            profile_picture=None,
            background_picture=None,
            is_active=True,
            is_admin=False,
        )

        # 3. Create user profile in DB
        profile = user_profile.create(db, owner_id=UUID(user_id), obj_in=profile_data)
        return {"message": "User created", "profile": profile}
    except Exception as e:
        # print(f"Error during sign-up: {e}")
        # raise HTTPException(status_code=400, detail=str(e))
        # Log real error for debugging
        logger.exception("Sign-up failed")
        # Use a safe fallback message if str(e) is empty
        msg = getattr(e, "detail", None) or str(e) or e.__class__.__name__
        raise HTTPException(status_code=400, detail=msg)
