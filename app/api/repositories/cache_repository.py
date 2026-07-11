import json

from app.api.database.redis import redis_client


class CacheRepository:
    def get(
        self,
        key: str,
    ) -> dict | list | None:

        value = redis_client.get(key)
        if value is None:
            return None

        return json.loads(value)


    def set(
        self,
        key: str,
        value: dict | list,
        expire: int = 300,
    ) -> None:

        redis_client.set(
            key,
            json.dumps(value),
            ex=expire,
        )


    def delete(
        self,
        key: str,
    ) -> None:

        redis_client.delete(key)


    def exists(
        self,
        key: str,
    ) -> bool:

        return bool(redis_client.exists(key))


    def delete_pattern(
        self,
        pattern: str,
    ) -> None:

        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            
            