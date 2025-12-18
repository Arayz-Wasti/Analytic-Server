from pydantic import BaseModel, Field

class TokenResponse(BaseModel):
    access_token: str = Field(..., examples=["ey...2kc"])
    refresh_token: str = Field(..., examples=["ey...2kc"])

