import pytest
import uuid
from app.db.session import init_db, SessionLocal
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.batch import RunBatch
from app.models.run import Run
from app.models.evaluation import Evaluation
from app.runner.batch_runner import batch_runner
from app.seeds.seed_data import LAPTOP_SCHEMA

@pytest.mark.asyncio
async def test_batch_runner_execution_and_evaluation():
    init_db()
    db = SessionLocal()
    try:
        # Create test task and config
        task = Task(
            id=str(uuid.uuid4()),
            name="Test Matrix",
            prompt_template="Find 3 laptops under $1200 with 16GB RAM",
            expected_output_schema=LAPTOP_SCHEMA,
            required_tools=["web_search"]
        )
        config = AgentConfig(
            id=str(uuid.uuid4()),
            name="Test Rigorous Agent",
            provider="mock",
            model="gpt-4o"
        )
        db.add(task)
        db.add(config)
        db.commit()

        batch = RunBatch(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_config_id=config.id,
            n_runs=3,
            concurrency_limit=2,
            status="pending"
        )
        db.add(batch)
        db.commit()

        # Execute batch
        await batch_runner.execute_batch(batch.id)

        # Refresh batch
        db.refresh(batch)
        assert batch.status == "completed"
        assert batch.completed_runs_count == 3
        assert batch.summary_metrics is not None
        assert "cost_per_successful_task" in batch.summary_metrics
        assert "overall_pass_rate" in batch.summary_metrics

        # Verify evaluations exist
        runs = db.query(Run).filter(Run.batch_id == batch.id).all()
        assert len(runs) == 3
        for r in runs:
            assert r.evaluation is not None
            assert r.evaluation.overall_score > 0
    finally:
        db.close()
