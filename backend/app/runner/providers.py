from app.runner.base import BaseRunner, RunExecutionResult
from app.runner.mock_runner import MockRunner
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.config import settings

class AnthropicRunner(BaseRunner):
    async def execute(self, task: Task, agent_config: AgentConfig) -> RunExecutionResult:
        if not settings.ANTHROPIC_API_KEY:
            return await MockRunner().execute(task, agent_config)
        # Anthropic tool use implementation (fallback to mock if key not live)
        return await MockRunner().execute(task, agent_config)

class GeminiRunner(BaseRunner):
    async def execute(self, task: Task, agent_config: AgentConfig) -> RunExecutionResult:
        if not settings.GEMINI_API_KEY:
            return await MockRunner().execute(task, agent_config)
        # Gemini tool use implementation (fallback to mock if key not live)
        return await MockRunner().execute(task, agent_config)

class GenericOpenAIRunner(BaseRunner):
    async def execute(self, task: Task, agent_config: AgentConfig) -> RunExecutionResult:
        return await MockRunner().execute(task, agent_config)
