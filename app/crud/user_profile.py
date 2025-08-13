import uuid
from sqlmodel import Session
from app.crud.base import CRUDBase
from app.models.user_profile import UserProfile, UserProfileCreate, UserProfileUpdate


class CRUDUserProfile(CRUDBase[UserProfile, UserProfileCreate, UserProfileUpdate]):
    def get_by_user_id(
        self, session: Session, *, user_id: uuid.UUID
    ) -> UserProfile | None:
        """Fetch the profile by its PK (user_id)."""
        return session.get(UserProfile, user_id)

    def create(
        self, session: Session, *, owner_id: uuid.UUID, obj_in: UserProfileCreate
    ) -> UserProfile:
        return super().create(session, owner_id=owner_id, obj_in=obj_in)

    def update(
        self, session: Session, *, id: uuid.UUID, obj_in: UserProfileUpdate
    ) -> UserProfile | None:
        return super().update(session, id=id, obj_in=obj_in)


user_profile = CRUDUserProfile(UserProfile)
