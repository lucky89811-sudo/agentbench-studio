from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ComparisonCreate(BaseModel):
    name: Optional[str] = None
    task_id: str
    agent_config_ids: list[str] = Field(..., min_length=2)
    n_runs_per_config: int = Field(default=5, ge=1, le=20)

class ComparisonRead(BaseModel):
    id: str
    name: str
    task_id: str
    batch_ids: list[str]
    metrics_matrix: dict[str, Any]
    statistical_confidence: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
