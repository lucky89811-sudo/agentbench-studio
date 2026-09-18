import asyncio
import uuid
from datetime import datetime, timezone
from app.db.session import init_db, SessionLocal
from app.seeds.seed_data import seed_database
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.batch import RunBatch
from app.models.comparison import Comparison
from app.runner.batch_runner import batch_runner
from app.services.comparison_service import comparison_service

async def populate_demo_benchmarks():
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)

        # Check if comparisons already exist
        if db.query(Comparison).count() > 0:
            print("Demo benchmarks already populated.")
            return

        laptop_task = db.query(Task).filter(Task.id == "task-laptop-matrix").first()
        rigorous_cfg = db.query(AgentConfig).filter(AgentConfig.id == "config-rigorous-v1").first()
        creative_cfg = db.query(AgentConfig).filter(AgentConfig.id == "config-creative-fast-v1").first()
        clinical_task = db.query(Task).filter(Task.id == "task-clinical-citation").first()

        print("Executing Demo Batch 1: Rigorous Agent on Laptop Matrix (N=5)...")
        b1 = RunBatch(
            id=str(uuid.uuid4()),
            task_id=laptop_task.id,
            agent_config_id=rigorous_cfg.id,
            n_runs=5,
            concurrency_limit=3,
            status="pending",
            created_at=datetime.now(timezone.utc)
        )
        db.add(b1)
        db.commit()
        await batch_runner.execute_batch(b1.id)

        print("Executing Demo Batch 2: Creative/Fast Agent on Laptop Matrix (N=5)...")
        b2 = RunBatch(
            id=str(uuid.uuid4()),
            task_id=laptop_task.id,
            agent_config_id=creative_cfg.id,
            n_runs=5,
            concurrency_limit=3,
            status="pending",
            created_at=datetime.now(timezone.utc)
        )
        db.add(b2)
        db.commit()
        await batch_runner.execute_batch(b2.id)

        print("Executing Demo Batch 3: Rigorous Agent on Clinical Trials (N=5)...")
        b3 = RunBatch(
            id=str(uuid.uuid4()),
            task_id=clinical_task.id,
            agent_config_id=rigorous_cfg.id,
            n_runs=5,
            concurrency_limit=3,
            status="pending",
            created_at=datetime.now(timezone.utc)
        )
        db.add(b3)
        db.commit()
        await batch_runner.execute_batch(b3.id)

        print("Creating pre-built Comparison between Rigorous vs Creative Agent...")
        comparison_service.build_comparison(
            db=db,
            task_id=laptop_task.id,
            batch_ids=[b1.id, b2.id],
            comparison_name="Laptop Matrix: Rigorous vs Fast & Creative Agent"
        )

        print("Demo benchmark data populated successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(populate_demo_benchmarks())
