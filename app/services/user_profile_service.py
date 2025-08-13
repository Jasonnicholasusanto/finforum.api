from typing import Optional
from uuid import UUID
from sqlmodel import Session
from app.models.user_profile import UserProfile
from app.schemas.user_profile import (
    UserProfileBase,
    UserProfileCreate,
    UserProfileUpdate,
)


# def get_user_profile(session: Session, user_id: UUID):
#     return session.exec(
#         select(UserProfileBase).where(UserProfileBase.user_id == user_id)
#     ).first()


def get_user_profile(session: Session, user_id: UUID) -> Optional[UserProfile]:
    """Fetch the profile by its PK (user_id)."""
    return session.get(UserProfile, user_id)


def create_user_profile(session: Session, profile: UserProfileCreate):
    db_profile = UserProfileBase(**profile.model_dump(exclude_unset=True))
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


def update_user_profile(
    session: Session, user_id: UUID, profile_update: UserProfileUpdate
):
    profile = get_user_profile(session, user_id)
    if not profile:
        return None
    update_data = profile_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile
