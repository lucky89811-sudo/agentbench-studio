from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class AgentConfigBase(BaseModel):
    name: str = Field(...)
    description: Optional[str] = None
    provider: str = Field(default="mock")  # openai, anthropic, gemini, generic, mock
    model: str = Field(default="gpt-4o")
    system_prompt: str = Field(default="")
    prompt_version: str = Field(default="v1.0.0")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    tool_definitions: list[dict[str, Any]] = Field(default_factory=list)
    max_steps: int = Field(default=8, ge=1, le=50)

class AgentConfigCreate(AgentConfigBase):
    pass

class AgentConfigUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    prompt_version: Optional[str] = None
    temperature: Optional[float] = None
    tool_definitions: Optional[list[dict[str, Any]]] = None
    max_steps: Optional[int] = None

class AgentConfigRead(AgentConfigBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
