from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from pwdlib import PasswordHash

from app.api.core.config import settings

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)

def hash_password(password:str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password:str,hashed_password:str) -> bool:
    return password_hash.verify(plain_password,hashed_password)


def create_access_token(data: dict) -> str:
    
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(
        minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    to_encode.update({'exp':expire})
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms = [settings.ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    
    except JWTError:
        raise ValueError("Invalid token")
    
    
def create_refresh_token(data: dict) -> str:
    
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    to_encode.update(
        {
            "exp": expire,
            "type": "refresh",
            "jti": str(uuid4()),
        }
    )

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )