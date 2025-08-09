from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.schemas.user_profile import UserProfileCreate
from app.services.auth import signup_user
from app.crud.user_profile import user_profile
from app.api.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def sign_up(user_in: UserProfileCreate, db: Session = Depends(get_db)):
    try:
        # 1. Create user in Supabase auth
        user = await signup_user(user_in.email, user_in.password)
        user_id = user.id  # Supabase auth user UUID

        # 2. Create user profile in your DB
        profile = user_profile.create_profile(db, user_id=user_id, obj_in=user_in)
        return {"message": "User created", "profile": profile}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
