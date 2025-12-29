from pydantic import BaseModel, EmailStr, Field
from typing import List, Literal


class SignupRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=6, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class PreferencesUpsertRequest(BaseModel):
    assets: List[str] = Field(min_length=1)
    investor_type: str = Field(min_length=1, max_length=50)
    content_types: List[str] = Field(min_length=1)


class PreferencesResponse(BaseModel):
    assets: List[str]
    investor_type: str
    content_types: List[str]


class MeResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    has_preferences: bool
