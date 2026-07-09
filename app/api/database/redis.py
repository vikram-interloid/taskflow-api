from redis import Redis

from app.api.core.config import settings

redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)