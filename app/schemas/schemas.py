from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class RequestLinkCreate(BaseModel):
    full_link: str
    expires_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "full_link": "https://example.com",
                "expires_at": "2025-02-09T13:19:21"
            }
        }

class ResponseLink(BaseModel):
    short_link: str
    full_link: str
    user_id: Optional[int] = None
    id: int
    created_at: datetime
    expires_at: Optional[datetime] = None


class RequestUserCreate(BaseModel):
    username: str
    password: str


class ResponseUser(BaseModel):
    id: int
    username: str
