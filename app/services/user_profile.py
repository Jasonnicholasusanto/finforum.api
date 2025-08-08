from uuid import UUID
from sqlmodel import Session, select
from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate


def get_user_profile(db: Session, user_id: UUID):
    return db.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()


def create_user_profile(db: Session, profile: UserProfileCreate):
    db_profile = UserProfile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def update_user_profile(db: Session, user_id: UUID, profile_update: UserProfileUpdate):
    profile = get_user_profile(db, user_id)
    if not profile:
        return None
    update_data = profile_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
