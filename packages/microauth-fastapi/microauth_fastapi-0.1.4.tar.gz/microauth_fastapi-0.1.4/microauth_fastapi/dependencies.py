from typing import Any
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED
from jose.exceptions import JWTError
from .auth import get_default_client, MicroAuthClient
import structlog


# Get logger
logger = structlog.get_logger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    client: MicroAuthClient = Depends(get_default_client)
) -> dict[str, Any]:
    """
    FastAPI dependency to retrieve and verify the current user.
    Usage:
        @app.get('/me')
        async def me(user=Depends(get_current_user)):
            return user
    """
    token = credentials.credentials
    try:
        payload = await client.verify_token(token)
    except JWTError as e:
        await logger.ainfo(f'Token verification failed with error: {str(e)}')
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f'Invalid or expired token.'
        )
    return payload
