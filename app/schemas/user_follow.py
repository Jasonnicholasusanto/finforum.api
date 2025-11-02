from pydantic import BaseModel

from app.schemas.user_profile import UserProfilePublic


class PaginatedFollowersResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[UserProfilePublic]
