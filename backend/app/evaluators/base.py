from abc import ABC, abstractmethod
from typing import Any
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from app.schemas.evaluation import EvaluatorResult

class BaseEvaluator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the evaluator."""
        pass

    @abstractmethod
    async def evaluate(self, task: Task, agent_config: AgentConfig, run: Run) -> EvaluatorResult:
        """Evaluate a single run against task and agent configuration."""
        pass
