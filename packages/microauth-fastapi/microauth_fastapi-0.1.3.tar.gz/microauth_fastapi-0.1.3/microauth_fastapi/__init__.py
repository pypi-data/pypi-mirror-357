from .config import Settings, _override_settings, _clear_override


def init(*,
         tenant_domain: str,
         client_id: str,
         algorithms: list[str] | None = None):
    """
    Programmatic initialization (overrides env vars).
    """
    # Clear cached env‐loaded settings
    _clear_override()
    # Create a new Settings instance and pin it
    override = Settings(
      tenant_domain=tenant_domain,
      client_id=client_id,
      algorithms=algorithms or ['RS256'],
    )
    _override_settings(override)
