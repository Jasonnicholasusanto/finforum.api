from sqlmodel import Session
from app.crud.base import CRUDBase
from app.models.user_profile import UserProfile, UserProfileCreate, UserProfileUpdate

class CRUDUserProfile(CRUDBase[UserProfile, UserProfileCreate, UserProfileUpdate]):
    def create_profile(self, session: Session, user_id: str, obj_in: UserProfileCreate) -> UserProfile:
        db_obj = UserProfile(user_id=user_id, **obj_in.dict())
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

user_profile = CRUDUserProfile(UserProfile)