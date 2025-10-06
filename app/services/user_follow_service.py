from uuid import UUID
from sqlalchemy import func, select
from sqlmodel import Session

from app.models.user_follow import UserFollow


def get_followers_count(session: Session, user_id: UUID) -> int:
    """
    Returns the number of users following the given user.
    """
    stmt = select(func.count()).select_from(UserFollow).where(UserFollow.following_id == user_id)
    result = session.exec(stmt).scalar() or 0
    return result


def get_following_count(session: Session, user_id: UUID) -> int:
    """
    Returns the number of users the given user is following.
    """
    stmt = select(func.count()).select_from(UserFollow).where(UserFollow.follower_id == user_id)
    result = session.exec(stmt).scalar() or 0
    return result


def is_following(session: Session, follower_id: UUID, following_id: UUID) -> bool:
    """
    Checks whether a user (follower_id) is following another user (following_id).
    """
    stmt = (
        select(UserFollow.id)
        .where(UserFollow.follower_id == follower_id, UserFollow.following_id == following_id)
        .limit(1)
    )
    return session.exec(stmt).first() is not None
