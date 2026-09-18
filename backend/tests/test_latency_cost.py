import pytest
from app.evaluators.latency_cost import LatencyCostTracker, calculate_cost
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from tests.fixtures.transcripts import VALID_LAPTOP_RUN

def test_cost_calculation_per_model():
    # gpt-4o: $2.50 / 1M input, $10.00 / 1M output
    cost = calculate_cost("gpt-4o", 100_000, 50_000)
    # (100_000 * 2.50 / 1M) + (50_000 * 10.00 / 1M) = 0.25 + 0.50 = 0.75
    assert cost == 0.75

@pytest.mark.asyncio
async def test_latency_cost_evaluator():
    evaluator = LatencyCostTracker()
    task = Task(
        id="task-1",
        name="Laptop Task",
        budget_constraints={"max_latency_ms": 2000.0, "max_cost_usd": 0.05}
    )
    config = AgentConfig(id="agent-1", name="Agent 1", model="gpt-4o")
    run = Run(
        id="run-valid",
        task_id="task-1",
        agent_config_id="agent-1",
        final_output=VALID_LAPTOP_RUN["final_output"],
        full_transcript=VALID_LAPTOP_RUN["transcript"],
        latency_ms=VALID_LAPTOP_RUN["latency_ms"],
        token_usage=VALID_LAPTOP_RUN["token_usage"],
        cost_usd=VALID_LAPTOP_RUN["cost_usd"]
    )

    result = await evaluator.evaluate(task, config, run)
    assert result.passed is True
    assert result.details["total_latency_ms"] == 950.0
    assert result.details["within_budget"] is True
