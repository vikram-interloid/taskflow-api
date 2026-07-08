from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.api.database.db_config import get_db
from app.api.services.auth_service import AuthService
from app.api.schemas.token_schema import TokenResponse, LoginRequest


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
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    return service.login(form_data)