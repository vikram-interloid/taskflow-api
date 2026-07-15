from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.core.limiter import limiter
from app.api.database.db_config import get_db
from app.api.schemas.token_schema import AccessTokenResponse, LoginRequest, RefreshTokenRequest, TokenResponse
from app.api.services.auth_service import AuthService

router = APIRouter(
    prefix = '/auth',
    tags = ["Authentication"]
)

oauthrouter = APIRouter(
    prefix = '/oauth',
    tags = ["Authentication"]
)

def get_auth_service(db: Session = Depends(get_db),) -> AuthService:
    return AuthService(db)

@oauthrouter.post(
    '/login',
     response_model=TokenResponse,
)
@limiter.limit("5/minute")
def oauth_login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    return service.auth_login(form_data)

@router.post(
    '/login',
    response_model=TokenResponse,
)
@limiter.limit("5/minute")
def login(
    request: Request,
    login_data: LoginRequest,
    # form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    return service.login(login_data)


@router.post(
    "/refresh",
    response_model = AccessTokenResponse,
)
@limiter.limit("5/minute")
def refresh_token(
    request: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
):
    return service.refresh_access_token(
        request.refresh_token
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("5/minute")
def logout(
    request: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
):
    service.logout(request.refresh_token)

    return Response(status_code = status.HTTP_204_NO_CONTENT)


