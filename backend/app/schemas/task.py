from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class TaskBase(BaseModel):
    name: str = Field(...)
    category: str = Field(default="tool-use")
    prompt_template: str = Field(...)
    expected_output_schema: Optional[dict[str, Any]] = None
    success_criteria: dict[str, Any] = Field(default_factory=dict)
    required_tools: list[str] = Field(default_factory=list)
    budget_constraints: Optional[dict[str, Any]] = Field(default_factory=dict)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    prompt_template: Optional[str] = None
    expected_output_schema: Optional[dict[str, Any]] = None
    success_criteria: Optional[dict[str, Any]] = None
    required_tools: Optional[list[str]] = None
    budget_constraints: Optional[dict[str, Any]] = None

class TaskRead(TaskBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
