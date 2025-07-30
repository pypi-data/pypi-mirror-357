"""Utility functions for authentication shared across API modules."""

import os
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Reusable HTTPBearer security scheme
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify that the provided Bearer token is in the allowed JWT_TOKENS list.

    Args:
        credentials: Parsed `Authorization` header credentials supplied by FastAPI's
            dependency injection using `HTTPBearer`.

    Raises:
        HTTPException: If the token is missing or not present in the allowed list.
    """
    jwt_tokens_env = os.getenv("JWT_TOKENS", "")
    tokens = [t.strip() for t in jwt_tokens_env.split("\n") if t.strip()]
    if credentials.credentials not in tokens:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True
