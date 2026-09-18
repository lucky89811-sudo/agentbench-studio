import pytest
from app.evaluators.tool_accuracy import ToolAccuracyEvaluator
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from tests.fixtures.transcripts import VALID_LAPTOP_RUN, IGNORED_TOOL_ERROR_RUN

@pytest.mark.asyncio
async def test_tool_accuracy_valid_run():
    evaluator = ToolAccuracyEvaluator()
    task = Task(id="task-1", name="Laptop Task", required_tools=["web_search"])
    config = AgentConfig(
        id="agent-1",
        name="Agent 1",
        tool_definitions=[
            {
                "name": "web_search",
                "parameters": {
                    "type": "object",
                    "required": ["query"],
                    "properties": {"query": {"type": "string"}}
                }
            }
        ]
    )
    run = Run(
        id="run-valid",
        task_id="task-1",
        agent_config_id="agent-1",
        final_output=VALID_LAPTOP_RUN["final_output"],
        full_transcript=VALID_LAPTOP_RUN["transcript"]
    )

    result = await evaluator.evaluate(task, config, run)
    assert result.passed is True
    assert result.score == 100.0
    assert result.details["ignored_tool_errors"] == 0
    assert result.details["missing_required_tools"] == []

@pytest.mark.asyncio
async def test_tool_accuracy_ignored_tool_error():
    evaluator = ToolAccuracyEvaluator()
    task = Task(id="task-1", name="Calculation Task", required_tools=["calculator"])
    config = AgentConfig(
        id="agent-1",
        name="Agent 1",
        tool_definitions=[{"name": "calculator"}]
    )
    run = Run(
        id="run-ignored",
        task_id="task-1",
        agent_config_id="agent-1",
        final_output=IGNORED_TOOL_ERROR_RUN["final_output"],
        full_transcript=IGNORED_TOOL_ERROR_RUN["transcript"]
    )

    result = await evaluator.evaluate(task, config, run)
    assert result.passed is False
    assert result.details["ignored_tool_errors"] >= 1
    assert result.details["tool_error_count"] >= 1
