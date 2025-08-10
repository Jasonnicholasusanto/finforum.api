import uuid
from sqlmodel import Session
from app.crud.base import CRUDBase
from app.models.user_profile import UserProfile, UserProfileCreate, UserProfileUpdate


class CRUDUserProfile(CRUDBase[UserProfile, UserProfileCreate, UserProfileUpdate]):
    def create(
        self, session: Session, *, owner_id: uuid.UUID, obj_in: UserProfileCreate
    ) -> UserProfile:
        return super().create(session, owner_id=owner_id, obj_in=obj_in)

    def update(
        self, session: Session, *, id: uuid.UUID, obj_in: UserProfileUpdate
    ) -> UserProfile | None:
        return super().update(session, id=id, obj_in=obj_in)

    # def create_profile(
    #     self, session: Session, user_id: str, obj_in: UserProfileCreate
    # ) -> UserProfile:
    #     db_obj = UserProfile(user_id=user_id, **obj_in.model_dump(exclude={"user_id"}))
    #     session.add(db_obj)
    #     session.commit()
    #     session.refresh(db_obj)
    #     return db_obj


user_profile = CRUDUserProfile(UserProfile)
