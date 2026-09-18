import pytest
from app.evaluators.hallucination import HallucinationDetector
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from tests.fixtures.transcripts import VALID_LAPTOP_RUN, PHANTOM_TOOL_RUN

@pytest.mark.asyncio
async def test_phantom_tool_detection():
    evaluator = HallucinationDetector()
    task = Task(id="task-1", name="Budget Task", prompt_template="Find a laptop and compute discount")
    config = AgentConfig(id="agent-1", name="Agent 1")
    run = Run(
        id="run-phantom",
        task_id="task-1",
        agent_config_id="agent-1",
        final_output=PHANTOM_TOOL_RUN["final_output"],
        full_transcript=PHANTOM_TOOL_RUN["transcript"]
    )

    result = await evaluator.evaluate(task, config, run)
    assert result.passed is False
    assert result.details["phantom_tool_use_count"] >= 2
    claimed_types = [p["claimed_tool_type"] for p in result.details["phantom_claims"]]
    assert "web_search" in claimed_types
    assert "calculator" in claimed_types

@pytest.mark.asyncio
async def test_no_phantom_tools_when_tools_actually_called():
    evaluator = HallucinationDetector()
    task = Task(id="task-1", name="Laptop Task", prompt_template="Find 3 laptops under $1200 with 16GB RAM under 2kg")
    config = AgentConfig(id="agent-1", name="Agent 1")
    run = Run(
        id="run-valid",
        task_id="task-1",
        agent_config_id="agent-1",
        final_output=VALID_LAPTOP_RUN["final_output"],
        full_transcript=VALID_LAPTOP_RUN["transcript"]
    )

    result = await evaluator.evaluate(task, config, run)
    assert result.details["phantom_tool_use_count"] == 0
    assert result.passed is True
