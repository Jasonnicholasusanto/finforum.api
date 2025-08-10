from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.schemas.auth import UserSignUp
from app.models.user_profile import UserProfileCreate
from app.services.auth import signup_user
from app.crud.user_profile import user_profile
from app.api.deps import get_db
import logging


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sign-up", tags=["sign-up"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def sign_up(user_in: UserSignUp, db: Session = Depends(get_db)):
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
