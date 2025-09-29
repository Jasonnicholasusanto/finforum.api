from __future__ import annotations
from sqlmodel import SQLModel
from app.schemas.user_activity import UserActivityPointsBreakdown, UserActivityPublic
from app.schemas.user_profile import UserProfileMe, UserProfilePublic


class UserDetailsResponse(SQLModel):
    profile: UserProfileMe
    activity: UserActivityPublic | None

class UserDetailsPublic(SQLModel):
    profile: UserProfilePublic
    points: UserActivityPointsBreakdown | None