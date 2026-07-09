from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.api.core.limiter import limiter

from app.api.database.db_config import get_db
from app.api.services.auth_service import AuthService
from app.api.schemas.token_schema import TokenResponse, AccessTokenResponse, RefreshTokenRequest


router = APIRouter(
    prefix = '/auth',
    tags = ["Authentication"]
)

def get_auth_service(db: Session = Depends(get_db),) -> AuthService:
    return AuthService(db)

@router.post(
    '/login',
     response_model=TokenResponse,
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    return service.login(form_data)


@router.post(
    "/refresh",
    response_model = AccessTokenResponse,
)
def refresh_token(
    request: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
):
    return service.refresh_access_token(
        request.refresh_token
    )
    
    
    
from fastapi import Response


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    request: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
):
    service.logout(request.refresh_token)

    return Response(status_code = status.HTTP_204_NO_CONTENT)


