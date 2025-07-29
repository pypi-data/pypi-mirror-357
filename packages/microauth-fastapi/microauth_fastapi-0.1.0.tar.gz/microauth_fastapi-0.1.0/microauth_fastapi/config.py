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


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings loader.
    Constructs the jwks_url if not explicitly set.
    """
    settings = Settings()
    if settings.jwks_url is None:
        settings.jwks_url = f'https://{settings.tenant_domain}/.well-known/jwks.json'
    return settings
