from __future__ import annotations

from pydantic import BaseModel
from app.schemas.user_activity import UserActivityPointsBreakdown, UserActivityPublic
from app.schemas.user_profile import UserProfileMe, UserProfilePublic


class UserDetailsResponse(BaseModel):
    profile: UserProfileMe
    activity: UserActivityPublic | None
    followers_count: int = 0
    following_count: int = 0


class UserDetailsPublic(BaseModel):
    profile: UserProfilePublic
    points: UserActivityPointsBreakdown | None
    followers_count: int = 0
    following_count: int = 0
