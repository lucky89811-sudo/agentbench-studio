import pytest
from app.evaluators.citation import CitationEvaluator
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from tests.fixtures.transcripts import CITATION_RUN

@pytest.mark.asyncio
async def test_citation_evaluator_identifies_broken_links():
    evaluator = CitationEvaluator()
    task = Task(id="task-1", name="Citation Task")
    config = AgentConfig(id="agent-1", name="Agent 1")
    run = Run(
        id="run-cit",
        task_id="task-1",
        agent_config_id="agent-1",
        final_output=CITATION_RUN["final_output"],
        full_transcript=CITATION_RUN["transcript"]
    )

    result = await evaluator.evaluate(task, config, run)
    assert result.details["total_citations"] == 2
    assert result.details["broken_link_count"] >= 1
    assert any("broken-link-example-404" in url for url in result.details["broken_links"])
    assert result.passed is False
