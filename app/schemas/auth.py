from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    reset_token: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=8, max_length=128)