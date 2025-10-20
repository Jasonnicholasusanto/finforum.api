from sqlmodel import SQLModel

from app.schemas.user_profile import UserProfilePublic


class PaginatedFollowersResponse(SQLModel):
    total: int
    limit: int
    offset: int
    data: list[UserProfilePublic]
