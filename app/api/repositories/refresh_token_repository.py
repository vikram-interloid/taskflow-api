from uuid import UUID

from app.api.database.redis import redis_client


class RefreshRepository:
    PREFIX = "taskflow:auth:refresh"

    def save_refresh_token(
        self,
        user_id: UUID,
        refresh_token: str,
        expire_seconds: int,
    ) -> None:

        redis_client.set(
            f"{self.PREFIX}:{user_id}",
            refresh_token,
            ex=expire_seconds,
        )

    def get_refresh_token(
        self,
        user_id: UUID,
    ) -> str | None:

        return redis_client.get(f"{self.PREFIX}:{user_id}")

    def delete_refresh_token(
        self,
        user_id: UUID,
    ) -> None:

        redis_client.delete(f"{self.PREFIX}:{user_id}")
