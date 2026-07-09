from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.core.security import decode_token
from app.api.repositories.user_repository import UserRepository
from app.api.database.db_config import SessionLocal
from uuid import UUID


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        request.state.user = None

        authorization = request.headers.get("Authorization")

        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]

            try:
                payload = decode_token(token)

                db = SessionLocal()

                try:
                    repository = UserRepository(db)

                    user = repository.get_user_by_id(
                        UUID(payload["sub"])
                    )

                    request.state.user = user

                finally:
                    db.close()

            except Exception:
                pass

        return await call_next(request)
    
    