from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class AdminResponse(BaseModel):
    id: str
    username: str
    is_active: bool


class LoginResponse(BaseModel):
    message: str
    admin: AdminResponse


class MeResponse(BaseModel):
    admin: AdminResponse