"""Dependency injection for FastAPI routes.

Provides reusable dependencies for:
- Database session management (async SQLAlchemy)
- Current user authentication (JWT)
- Rate limiting
- Redis cache client
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from evidence_ai.config import settings
from evidence_ai.db.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# JWT bearer scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator:
    """Yield an async SQLAlchemy session.

    Usage::

        @router.get("/reviews")
        async def list_reviews(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    """Validate JWT bearer token and return current user info.

    In development (app_env != production), authentication is bypassed
    and a test user is returned.

    Usage::

        @router.post("/reviews")
        async def create_review(user=Depends(get_current_user)):
            ...
    """
    if not settings.is_production:
        # Development bypass
        return {"user_id": "dev-user", "email": "dev@evidenceai.com", "role": "admin"}

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        from jose import JWTError, jwt

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
        return {"user_id": user_id, "email": payload.get("email"), "role": payload.get("role")}

    except Exception as e:
        logger.debug("JWT validation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_redis():  # noqa: ANN201
    """Yield a Redis client connection.

    Returns None if Redis is not configured (cache is disabled).

    Usage::

        @router.get("/evidence/{id}")
        async def get_evidence(id: str, redis=Depends(get_redis)):
            ...
    """
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        try:
            yield client
        finally:
            await client.aclose()
    except ImportError:
        yield None
    except Exception as e:
        logger.warning("Redis connection failed: %s. Cache disabled.", e)
        yield None
