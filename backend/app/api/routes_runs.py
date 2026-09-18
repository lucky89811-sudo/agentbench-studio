import asyncio
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.batch import RunBatch
from app.models.run import Run
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.evaluation import Evaluation
from app.schemas.batch import BatchCreate, BatchRead
from app.schemas.run import RunRead
from app.runner.batch_runner import batch_runner

router = APIRouter(prefix="/runs", tags=["Runs & Batches"])

@router.post("/batch", response_model=BatchRead)
def create_and_start_batch(
    payload: BatchCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == payload.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    config = db.query(AgentConfig).filter(AgentConfig.id == payload.agent_config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Agent Config not found")

    batch_id = str(uuid.uuid4())
    batch = RunBatch(
        id=batch_id,
        task_id=payload.task_id,
        agent_config_id=payload.agent_config_id,
        n_runs=payload.n_runs,
        concurrency_limit=payload.concurrency_limit,
        status="pending",
        created_at=datetime.now(timezone.utc)
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    # Launch batch execution in background
    background_tasks.add_task(batch_runner.execute_batch, batch_id)

    return batch

@router.get("/batch", response_model=list[BatchRead])
def list_batches(db: Session = Depends(get_db)):
    return (
        db.query(RunBatch)
        .options(joinedload(RunBatch.task), joinedload(RunBatch.agent_config))
        .order_by(RunBatch.created_at.desc())
        .all()
    )

@router.get("/batch/{batch_id}", response_model=BatchRead)
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    batch = (
        db.query(RunBatch)
        .options(
            joinedload(RunBatch.task),
            joinedload(RunBatch.agent_config),
            joinedload(RunBatch.runs).joinedload(Run.evaluation)
        )
        .filter(RunBatch.id == batch_id)
        .first()
    )
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

@router.get("/{run_id}", response_model=RunRead)
def get_single_run(run_id: str, db: Session = Depends(get_db)):
    run = (
        db.query(Run)
        .options(joinedload(Run.evaluation))
        .filter(Run.id == run_id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
