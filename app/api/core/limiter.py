from slowapi import Limiter

from app.api.core.config import settings
from app.api.core.rate_limit_key import rate_limit_key

limiter = Limiter(
    key_func = rate_limit_key,
    storage_uri=settings.REDIS_URL,
)
