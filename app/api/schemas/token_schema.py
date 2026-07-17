from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(extra="forbid")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict(extra="forbid")


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)
