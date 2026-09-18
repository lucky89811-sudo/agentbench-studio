from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field
from app.models.task import Task
from app.models.agent_config import AgentConfig

class RunExecutionResult(BaseModel):
    transcript: list[dict[str, Any]] = Field(default_factory=list)
    final_output: str = ""
    latency_ms: float = 0.0
    time_to_first_token_ms: float = 0.0
    token_usage: dict[str, int] = Field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
    cost_usd: float = 0.0
    error_trace: Optional[str] = None
    status: str = "completed"

class BaseRunner(ABC):
    @abstractmethod
    async def execute(self, task: Task, agent_config: AgentConfig) -> RunExecutionResult:
        """Executes a single run of the task with the given agent configuration."""
        pass
