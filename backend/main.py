"""Root backend entrypoint wrapper for backwards compatibility."""

from backend.api.main import app

__all__ = ["app"]
