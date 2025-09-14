import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from supabase import create_async_client
from supabase._async.client import AsyncClient

from app.core.config import settings
from app.schemas.auth import UserIn

logger = logging.getLogger(__name__)

# Simple Bearer token scheme (Swagger will show a single token box)
bearer = HTTPBearer(auto_error=True)


async def get_supabase_anon_client() -> AsyncClient:
    """
    Create an anon-key Supabase client.
    Safe for serverless: cheap to construct and uses HTTPS (no DB sockets).
    """
    return await create_async_client(settings.SUPABASE_URL, settings.SUPABASE_KEY_ANON)


TokenCreds = Annotated[HTTPAuthorizationCredentials, Depends(bearer)]
SupabaseAnon = Annotated[AsyncClient, Depends(get_supabase_anon_client)]


async def get_current_user(
    creds: TokenCreds,
    supabase_client: SupabaseAnon,
) -> UserIn:
    """
    Validate the JWT and return the current user.
    Uses anon client + user token (no service-role needed).
    """
    token = creds.credentials
    try:
        res = await supabase_client.auth.get_user(jwt=token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    if not res or not res.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    return UserIn(**res.user.model_dump(), access_token=token)


bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user_id(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """
    Validates Supabase JWT (HS256) and returns user id (auth_id) from 'sub' claim.
    """
    try:
        payload = jwt.decode(
            token.credentials,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={
                "verify_aud": False
            },  # Supabase sets 'aud', but we don't require checking here
        )
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("No 'sub' in token")
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
        )
