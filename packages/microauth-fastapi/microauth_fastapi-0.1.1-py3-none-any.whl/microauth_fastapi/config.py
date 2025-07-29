from functools import lru_cache
from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """
    Application settings for MicroAuth integration.
    Reads from environment variables prefixed with MICROAUTH_.
    """
    tenant_domain: str = Field(..., description='Your MicroAuth tenant domain, e.g. auth.microauth.com')
    client_id: str = Field(..., description='Your MicroAuth OAuth client ID.')
    algorithms: List[str] = ['RS256']
    jwks_url: Optional[AnyUrl] = None

    class Config:
        env_prefix = 'MICROAUTH_'
        env_file = '.env'


_override: Settings | None = None


def _override_settings(s: 'Settings') -> None:
    global _override
    _override = s


def _clear_override() -> None:
    global _override
    _override = None


@lru_cache()
def get_settings() -> Settings:
    if _override:
        return _override
    s = Settings()
    if not s.jwks_url:
        s.jwks_url = f'https://{s.tenant_domain}/.well-known/jwks.json'
    return s
