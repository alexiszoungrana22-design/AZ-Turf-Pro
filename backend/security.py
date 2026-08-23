"""AZ Turf Pro - sécurité centralisée admin / Premium."""
import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timedelta, timezone

from fastapi import Header, HTTPException

ADMIN_KEY_NAMES = (
    "AZ_ADMIN_API_KEY",
    "AZ_TURF_ADMIN_API_KEY",
    "AZ_TURF_ADMIN_KEY",
    "ADMIN_API_KEY",
    "ADMIN_KEY",
)
ADMIN_SESSION_SECRET = os.getenv("AZ_ADMIN_SESSION_SECRET", "").strip()
PREMIUM_ACCESS_SECRET = os.getenv("AZ_PREMIUM_ACCESS_SECRET", "").strip()
ADMIN_SESSION_TTL = int(os.getenv("AZ_ADMIN_SESSION_TTL", "1800"))


def configured_admin_keys() -> list[str]:
    keys=[]
    for name in ADMIN_KEY_NAMES:
        value=os.getenv(name, "").strip()
        if value and value not in keys:
            keys.append(value)
    return keys


def is_valid_admin_key(value: str | None) -> bool:
    supplied=(value or "").strip()
    return bool(supplied and any(hmac.compare_digest(supplied, key) for key in configured_admin_keys()))


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_admin_session() -> tuple[str, int]:
    if not ADMIN_SESSION_SECRET:
        raise HTTPException(status_code=503, detail="AZ_ADMIN_SESSION_SECRET n'est pas configurée sur le serveur.")
    exp=int(time.time()) + max(300, ADMIN_SESSION_TTL)
    payload={"role":"admin", "iat":int(time.time()), "exp":exp}
    encoded=_b64(json.dumps(payload,separators=(",",":"),ensure_ascii=False).encode())
    signature=hmac.new(ADMIN_SESSION_SECRET.encode(), encoded.encode(), hashlib.sha256).digest()
    return encoded+"."+_b64(signature), exp


def verify_admin_session(token: str | None) -> bool:
    if not ADMIN_SESSION_SECRET or not token or "." not in token:
        return False
    try:
        encoded, signature=token.split(".",1)
        expected=hmac.new(ADMIN_SESSION_SECRET.encode(), encoded.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _unb64(signature)):
            return False
        payload=json.loads(_unb64(encoded).decode())
        return payload.get("role") == "admin" and int(payload.get("exp",0)) > int(time.time())
    except Exception:
        return False


def require_admin(
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    x_admin_session: str | None = Header(default=None, alias="X-Admin-Session"),
) -> str:
    if not configured_admin_keys():
        raise HTTPException(status_code=503, detail="Accès administrateur indisponible : aucune clé serveur n'est configurée.")
    if verify_admin_session(x_admin_session):
        return "admin"
    if is_valid_admin_key(x_admin_key):
        return "admin"
    raise HTTPException(status_code=401, detail="Accès administrateur non autorisé.")


def create_premium_token(telephone: str, date_fin: str) -> str:
    if not PREMIUM_ACCESS_SECRET:
        raise HTTPException(status_code=503, detail="AZ_PREMIUM_ACCESS_SECRET n'est pas configurée.")
    try:
        exp=int(datetime.fromisoformat(date_fin).timestamp())
    except Exception:
        raise HTTPException(status_code=500, detail="Date d'expiration Premium invalide.")
    payload={"telephone":telephone.strip(),"exp":exp,"role":"premium"}
    encoded=_b64(json.dumps(payload,separators=(",",":"),ensure_ascii=False).encode())
    signature=hmac.new(PREMIUM_ACCESS_SECRET.encode(), encoded.encode(), hashlib.sha256).digest()
    return encoded+"."+_b64(signature)


def verify_premium_token(token: str) -> dict:
    if not PREMIUM_ACCESS_SECRET or not token or "." not in token:
        raise HTTPException(status_code=401, detail="Accès Premium non autorisé.")
    try:
        encoded, signature=token.split(".",1)
        expected=hmac.new(PREMIUM_ACCESS_SECRET.encode(), encoded.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _unb64(signature)):
            raise ValueError("signature")
        payload=json.loads(_unb64(encoded).decode())
        if payload.get("role") != "premium" or not str(payload.get("telephone","")).strip() or int(payload.get("exp",0)) <= int(time.time()):
            raise ValueError("expiration")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Accès Premium non autorisé.")
