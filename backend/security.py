from fastapi import Header, HTTPException

from config import ADMIN_API_KEY


def require_admin(x_admin_key: str | None = Header(default=None)):
    """Protège les routes d'administration lorsque AZ_ADMIN_API_KEY est configurée."""
    if not ADMIN_API_KEY:
        return {
            "authenticated": False,
            "mode": "compatibilite",
            "warning": "AZ_ADMIN_API_KEY n'est pas configurée."
        }

    if not x_admin_key or x_admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Accès administrateur non autorisé.")

    return {"authenticated": True, "mode": "api_key"}
