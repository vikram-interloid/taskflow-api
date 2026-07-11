from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
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
    
    expire = datetime.now(UTC) + timedelta(
        minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    to_encode.update({'exp':expire, 'type':'access'})
    
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
    except ExpiredSignatureError as err:
        raise ValueError("Token has expired")from err
    
    except JWTError as err :
        raise ValueError("Invalid token") from err
    
    
def create_refresh_token(data: dict) -> str:
    
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(
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
    
