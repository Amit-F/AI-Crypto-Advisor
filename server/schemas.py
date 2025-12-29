from pydantic import BaseModel, EmailStr, Field
from typing import Any, List, Literal, Optional
from datetime import date



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

class VoteRequest(BaseModel):
    dashboard_item_id: int
    value: int = Field(..., ge=-1, le=1)

class VoteResponse(BaseModel):
    dashboard_item_id: int
    value: int

class DashboardItemResponse(BaseModel):
    id: int
    item_type: Literal["news", "prices", "ai", "meme"]
    payload: Any
    user_vote: Optional[int] = None  # -1, 1, or null

class DashboardResponse(BaseModel):
    date: date
    items: List[DashboardItemResponse]
