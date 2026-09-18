from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.evaluation import EvaluationRead

class RunStep(BaseModel):
    step_index: int
    timestamp: str
    role: str  # user, assistant, system, tool
    content: Optional[str] = None
    tool_calls: Optional[list[dict[str, Any]]] = None
    tool_results: Optional[list[dict[str, Any]]] = None
    step_latency_ms: Optional[float] = 0.0

class RunRead(BaseModel):
    id: str
    batch_id: Optional[str] = None
    task_id: str
    agent_config_id: str
    run_index: int
    status: str
    full_transcript: list[dict[str, Any]]
    final_output: str
    latency_ms: float
    time_to_first_token_ms: float
    token_usage: dict[str, Any]
    cost_usd: float
    error_trace: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    evaluation: Optional[EvaluationRead] = None

    model_config = ConfigDict(from_attributes=True)
