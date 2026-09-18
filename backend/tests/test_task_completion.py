import pytest
from unittest.mock import MagicMock
from app.evaluators.task_completion import TaskCompletionEvaluator
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from tests.fixtures.transcripts import LAPTOP_TASK_SCHEMA, VALID_LAPTOP_RUN, SCHEMA_VIOLATION_RUN

@pytest.mark.asyncio
async def test_schema_validation_passes():
    evaluator = TaskCompletionEvaluator()
    task = Task(id="task-1", name="Laptop Task", expected_output_schema=LAPTOP_TASK_SCHEMA)
    config = AgentConfig(id="agent-1", name="Agent 1")
    run = Run(
        id="run-1",
        task_id="task-1",
        agent_config_id="agent-1",
        final_output=VALID_LAPTOP_RUN["final_output"],
        full_transcript=VALID_LAPTOP_RUN["transcript"]
    )

    result = await evaluator.evaluate(task, config, run)
    assert result.passed is True
    assert result.score == 100.0
    assert result.details["mode"] == "deterministic_schema"
    assert len(result.details["validation_errors"]) == 0

@pytest.mark.asyncio
async def test_schema_validation_fails_on_missing_fields_and_count():
    evaluator = TaskCompletionEvaluator()
    task = Task(id="task-1", name="Laptop Task", expected_output_schema=LAPTOP_TASK_SCHEMA)
    config = AgentConfig(id="agent-1", name="Agent 1")
    run = Run(
        id="run-2",
        task_id="task-1",
        agent_config_id="agent-1",
        final_output=SCHEMA_VIOLATION_RUN["final_output"],
        full_transcript=SCHEMA_VIOLATION_RUN["transcript"]
    )

    result = await evaluator.evaluate(task, config, run)
    assert result.passed is False
    assert result.score < 100.0
    assert len(result.details["validation_errors"]) > 0

@pytest.mark.asyncio
async def test_schema_validation_fails_on_non_json_output():
    evaluator = TaskCompletionEvaluator()
    task = Task(id="task-1", name="Laptop Task", expected_output_schema=LAPTOP_TASK_SCHEMA)
    config = AgentConfig(id="agent-1", name="Agent 1")
    run = Run(
        id="run-3",
        task_id="task-1",
        agent_config_id="agent-1",
        final_output="I could not find any laptops sorry!",
        full_transcript=[]
    )

    result = await evaluator.evaluate(task, config, run)
    assert result.passed is False
    assert result.score == 0.0
