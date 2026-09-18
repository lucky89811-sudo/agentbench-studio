from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class EvaluatorResult(BaseModel):
    metric: str
    score: float = Field(..., ge=0.0, le=100.0)
    passed: bool
    evidence: str
    details: dict[str, Any] = Field(default_factory=dict)

class EvaluationRead(BaseModel):
    id: str
    run_id: str
    overall_passed: bool
    overall_score: float

    # Evaluator metrics
    completion_rate: bool
    completion_score: float
    completion_details: dict[str, Any]

    tool_call_accuracy: float
    tool_error_count: int
    unnecessary_tool_calls: int
    ignored_tool_errors: int
    tool_details: dict[str, Any]

    citation_precision: float
    uncited_claims_count: int
    broken_link_count: int
    citation_details: dict[str, Any]

    hallucination_rate: float
    phantom_tool_use_count: int
    hallucination_details: dict[str, Any]

    latency_details: dict[str, Any]
    cost_details: dict[str, Any]

    raw_evaluator_results: list[dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
