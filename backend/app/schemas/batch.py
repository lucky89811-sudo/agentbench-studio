from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.run import RunRead
from app.schemas.task import TaskRead
from app.schemas.agent_config import AgentConfigRead

class BatchCreate(BaseModel):
    task_id: str
    agent_config_id: str
    n_runs: int = Field(default=5, ge=1, le=50)
    concurrency_limit: int = Field(default=3, ge=1, le=10)

class BatchRead(BaseModel):
    id: str
    task_id: str
    agent_config_id: str
    n_runs: int
    concurrency_limit: int
    status: str
    completed_runs_count: int
    failed_runs_count: int
    summary_metrics: Optional[dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    task: Optional[TaskRead] = None
    agent_config: Optional[AgentConfigRead] = None
    runs: Optional[list[RunRead]] = None

    model_config = ConfigDict(from_attributes=True)
