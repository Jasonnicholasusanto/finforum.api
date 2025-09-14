import uuid
from sqlmodel import Session

from app.crud.base import CRUDBase
from app.models.user_activity import UserActivity
from app.schemas.user_activity import UserActivityCreate, UserActivityUpdate


class CRUDUserActivity(CRUDBase[UserActivity, UserActivityCreate, UserActivityUpdate]):
    def get_by_user_id(
        self, session: Session, *, user_id: uuid.UUID
    ) -> UserActivity | None:
        """Fetch the user_activity row by its PK (user_id)."""
        return session.get(UserActivity, user_id)

    def create(
        self, session: Session, *, owner_id: uuid.UUID, obj_in: UserActivityCreate
    ) -> UserActivity:
        db_obj = UserActivity(**obj_in.model_dump(exclude_unset=True))
        db_obj.user_id = owner_id
        session.add(db_obj)
        session.flush()
        return db_obj

    def update(
        self, session: Session, *, id: uuid.UUID, obj_in: UserActivityUpdate
    ) -> UserActivity | None:
        return super().update(session, id=id, obj_in=obj_in)


user_activity = CRUDUserActivity(UserActivity)
