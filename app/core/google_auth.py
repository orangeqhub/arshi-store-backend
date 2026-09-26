import time

import httpx
from jose import jwt, JWTError

from app.core.config import settings


GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = ("accounts.google.com", "https://accounts.google.com")

# Google rotates its signing keys; cache them for the duration it advertises.
_jwks_cache = {"keys": None, "expires_at": 0.0}


async def _get_google_jwks(force_refresh: bool = False):

    now = time.time()

    if (
        not force_refresh
        and _jwks_cache["keys"]
        and now < _jwks_cache["expires_at"]
    ):
        return _jwks_cache["keys"]

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(GOOGLE_CERTS_URL)
        response.raise_for_status()

    max_age = 3600
    cache_control = response.headers.get("cache-control", "")
    for part in cache_control.split(","):
        part = part.strip()
        if part.startswith("max-age="):
            try:
                max_age = int(part.split("=", 1)[1])
            except ValueError:
                pass

    _jwks_cache["keys"] = response.json()
    _jwks_cache["expires_at"] = now + max_age

    return _jwks_cache["keys"]


async def verify_google_id_token(id_token: str) -> dict:
    """
    Verify a Google Identity Services ID token (the `credential` returned
    by the Sign in with Google button) and return its claims.

    Raises ValueError if the token is invalid.
    """

    header = jwt.get_unverified_header(id_token)
    jwks = await _get_google_jwks()

    # Key rotated since we cached -> refetch once
    if not any(k.get("kid") == header.get("kid") for k in jwks.get("keys", [])):
        jwks = await _get_google_jwks(force_refresh=True)

    try:
        claims = jwt.decode(
            id_token,
            jwks,
            algorithms=["RS256"],
            audience=settings.GOOGLE_CLIENT_ID,
            options={"verify_at_hash": False},
        )
    except JWTError as e:
        raise ValueError(f"Invalid Google token: {e}")

    if claims.get("iss") not in GOOGLE_ISSUERS:
        raise ValueError("Invalid Google token issuer")

    if not claims.get("email"):
        raise ValueError("Google account has no email")

    if not claims.get("email_verified"):
        raise ValueError("Google email is not verified")

    return claims
