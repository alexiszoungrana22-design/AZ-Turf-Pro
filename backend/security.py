from fastapi import Header, HTTPException
from config import ADMIN_API_KEY


def require_admin(x_admin_key: str | None = Header(default=None)):
    """Refuse toute route admin si la clé serveur n'est pas configurée ou incorrecte."""
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Accès administrateur indisponible : AZ_ADMIN_API_KEY n'est pas configurée."
        )

    if not x_admin_key or x_admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Accès administrateur non autorisé."
        )

    return True
