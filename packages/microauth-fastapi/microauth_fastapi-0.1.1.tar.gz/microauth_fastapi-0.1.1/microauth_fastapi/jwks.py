import time
import httpx
from typing import Any, Dict

# Module‐level cache
_jwks_cache: Dict[str, Any] = {}
_jwks_expiry: float = 0.0


async def get_jwks(jwks_url: str, ttl: int = 3600) -> Dict[str, Any]:
    """
    Fetches and caches the JWKS payload for ttl seconds.
    """
    global _jwks_cache, _jwks_expiry
    now = time.time()
    if not _jwks_cache or now >= _jwks_expiry:
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url, timeout=5.0)
            response.raise_for_status()
            _jwks_cache = response.json()
            _jwks_expiry = now + ttl
    return _jwks_cache
