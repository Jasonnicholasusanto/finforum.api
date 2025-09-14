from typing import Optional
import uuid

from sqlmodel import Session

from app.crud.user_activity import user_activity as user_activity_crud
from app.models.user_activity import UserActivity
from app.schemas.user_activity import UserActivityCreate, UserActivityPointsBreakdown, UserActivityPublic


def get_user_activity(
    session: Session, *, profile_id: uuid.UUID
) -> Optional[UserActivity]:
    """
    Return the ORM row for a given profile_id (FK = user_profile.id), or None.
    """
    return user_activity_crud.get_by_user_id(session, user_id=profile_id)

def get_user_points(
    session: Session, *, profile_id: uuid.UUID
) -> Optional[UserActivityPointsBreakdown]:
    """
    Return the total_points for a given profile_id (FK = user_profile.id), or 0 if no activity.
    """
    ua = get_user_activity(session, profile_id=profile_id)
    if not ua:
        return UserActivityPointsBreakdown(
            total_points=0,
            weekly_points=0,
            monthly_points=0,
        )

    return UserActivityPointsBreakdown(
        total_points=int(ua.total_points or 0),
        weekly_points=int(ua.weekly_points or 0),
        monthly_points=int(ua.monthly_points or 0),
    )


def get_user_activity_public(
    session: Session, *, profile_id: uuid.UUID
) -> Optional[UserActivityPublic]:
    """
    Return a serialized public schema for a given profile_id, or None.
    """
    row = get_user_activity(session, profile_id=profile_id)
    return (
        UserActivityPublic.model_validate(row, from_attributes=True)
        if row
        else None
    )

def create_user_activity(
    session: Session, *, profile_id: uuid.UUID, obj_in: UserActivityCreate
) -> UserActivityPublic:
    """
    Create a user_activity row for the given user_profile id (FK = user_profile.id).
    """
    db_obj = user_activity_crud.create(session, owner_id=profile_id, obj_in=obj_in)
    return UserActivityPublic.model_validate(db_obj, from_attributes=True)