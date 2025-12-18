from datetime import datetime
from pydantic import BaseModel, Field

class CreateUserRequest(BaseModel):
    username: str = Field(..., description="Username of the user")
    email: str = Field(..., description="Email address of the user", example="arayz11@gmail.com")
    password: str = Field(..., description="Password of the user", example="12223112")
    is_active: bool | None = Field(default=True, description="Is the user active?")
    created_at: datetime | None = Field(default=None, description="Created at")

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username of the user")
    email: str | None = Field(None, description="Email address of the user")
    password: str = Field(..., description="Password of the user")