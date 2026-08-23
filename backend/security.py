import base64
import hashlib
import hmac
import json
import time

from fastapi import Header, HTTPException

from config import ADMIN_API_KEY, PREMIUM_ACCESS_SECRET


def is_valid_admin_key(x_admin_key: str | None) -> bool:
    return bool(ADMIN_API_KEY and x_admin_key and hmac.compare_digest(x_admin_key, ADMIN_API_KEY))


def require_admin(x_admin_key: str | None = Header(default=None)):
    """Refuse toute route admin si la clé serveur n'est pas configurée ou incorrecte."""
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Accès administrateur indisponible : AZ_ADMIN_API_KEY n'est pas configurée."
        )

    if not is_valid_admin_key(x_admin_key):
        raise HTTPException(
            status_code=401,
            detail="Accès administrateur non autorisé."
        )

    return True


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_premium_token(telephone: str, date_fin: str) -> str:
    """Crée un jeton Premium signé. Aucun secret n'est exposé au navigateur."""
    if not PREMIUM_ACCESS_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Accès Premium indisponible : AZ_PREMIUM_ACCESS_SECRET n'est pas configurée."
        )

    try:
        exp = int(__import__('datetime').datetime.fromisoformat(date_fin).timestamp())
    except Exception:
        raise HTTPException(status_code=500, detail="Date d'expiration Premium invalide.")

    payload = {"telephone": telephone.strip(), "exp": exp}
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()
    encoded = _b64(raw)
    signature = hmac.new(PREMIUM_ACCESS_SECRET.encode(), encoded.encode(), hashlib.sha256).digest()
    return encoded + "." + _b64(signature)


def verify_premium_token(token: str) -> dict:
    """Vérifie intégrité et expiration du jeton Premium."""
    if not PREMIUM_ACCESS_SECRET or not token or "." not in token:
        raise HTTPException(status_code=401, detail="Accès Premium non autorisé.")

    try:
        encoded, signature = token.split(".", 1)
        expected = hmac.new(PREMIUM_ACCESS_SECRET.encode(), encoded.encode(), hashlib.sha256).digest()
        supplied = _unb64(signature)
        if not hmac.compare_digest(expected, supplied):
            raise ValueError("signature")

        payload = json.loads(_unb64(encoded).decode())
        telephone = str(payload.get("telephone", "")).strip()
        exp = int(payload.get("exp", 0))
        if not telephone or exp <= int(time.time()):
            raise ValueError("expiration")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Accès Premium non autorisé.")
