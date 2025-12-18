from datetime import datetime
from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel, Field

class Source(str, Enum):
    web = "web"
    mobile = "mobile"
    backend = "backend"
    ios = "ios"
    android = "android"

class Event(BaseModel):
    event_name: str = Field(...)
    event_category: str = Field(...)
    user_id: Optional[str] = Field(...)
    session_id: Optional[str] = Field(...)
    source: Source = Field(...)  # web, mobile, backend
    metadata: Dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Metric(BaseModel):
    metric_name: str = Field(...)
    value: float = Field(...)
    unit: str = Field(...)
    tags: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EventCreate(BaseModel):
    event_name: str
    event_category: str
    source: Source = Field(...)
    user_id: Optional[str]
    session_id: Optional[str]
