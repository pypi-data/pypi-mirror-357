from pydantic import BaseModel, Field
from datetime import datetime, timezone                                                                                                                             
from typing import Dict, List, Optional, Any

class ContextMetadata(BaseModel):
    client: str
    content: str

class MemoryData(BaseModel):
    id: int
    content: str
    metadata: ContextMetadata
    distance: float

class ContextResponse(BaseModel):
    success: bool
    message: str
    data: List[MemoryData]
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )

#Temporary context data structure
class ContextData(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ContextQuery(BaseModel):
    query: Optional[str] = None
    k: Optional[int] = 3
    filters: Optional[Dict[str, Any]] = {}


class HealthCheck(BaseModel):
    status: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
    connected: bool

class AgentList(BaseModel):
    agent_name: str
    status: str
