from jose import jwt
from jose.exceptions import JWTError
from typing import Dict, List, Any
from .jwks import get_jwks
from microauth_fastapi.config import get_settings


class MicroAuthClient:
    """
    Client for verifying JWT tokens issued by MicroAuth IdP.
    """
    def __init__(
        self,
        domain: str,
        audience: str,
        algorithms: List[str],
        jwks_url: str
    ):
        self.domain = domain
        self.audience = audience
        self.algorithms = algorithms
        self.jwks_url = jwks_url

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verifies the JWT and returns its payload.
        Raises JWTError on failure.
        """
        jwks = await get_jwks(self.jwks_url)
        unverified_header = jwt.get_unverified_header(token)

        # Locate the key by kid
        key = next(
            (k for k in jwks.get('keys', []) if k.get('kid') == unverified_header.get('kid')),
            None
        )
        if not key:
            raise JWTError('Unable to find matching JWK key')

        # Decode and validate
        payload = jwt.decode(
            token,
            key,
            algorithms=unverified_header.get('alg'),
            audience=self.audience,
            issuer=f'https://{self.domain}'
        )
        return payload


# Helper to get a default client via settings
async def get_default_client() -> MicroAuthClient:
    settings = get_settings()
    return MicroAuthClient(
        domain=settings.tenant_domain,
        audience=settings.client_id,
        algorithms=settings.algorithms,
        jwks_url=str(settings.jwks_url)
    )
