from slowapi import Limiter

from app.api.core.config import settings
from app.api.core.rate_limit_key import rate_limit_key

limiter = Limiter(
    key_func = rate_limit_key,
    storage_uri=(f'redis://{settings.REDIS_USERNAME}:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}')
)
