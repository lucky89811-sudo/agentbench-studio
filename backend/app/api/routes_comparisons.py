import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.comparison import Comparison
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.batch import RunBatch
from app.schemas.comparison import ComparisonCreate, ComparisonRead
from app.services.comparison_service import comparison_service
from app.runner.batch_runner import batch_runner

router = APIRouter(prefix="/comparisons", tags=["Comparisons"])

@router.get("", response_model=list[ComparisonRead])
def list_comparisons(db: Session = Depends(get_db)):
    return db.query(Comparison).order_by(Comparison.created_at.desc()).all()

@router.get("/{comparison_id}", response_model=ComparisonRead)
def get_comparison(comparison_id: str, db: Session = Depends(get_db)):
    comp = db.query(Comparison).filter(Comparison.id == comparison_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Comparison not found")
    return comp

@router.post("", response_model=ComparisonRead)
async def create_comparison(
    payload: ComparisonCreate,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == payload.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    batch_ids = []
    # For each config, find latest completed batch or create and execute one
    for cfg_id in payload.agent_config_ids:
        cfg = db.query(AgentConfig).filter(AgentConfig.id == cfg_id).first()
        if not cfg:
            continue
        
        batch = db.query(RunBatch).filter(
            RunBatch.task_id == payload.task_id,
            RunBatch.agent_config_id == cfg_id,
            RunBatch.status == "completed"
        ).order_by(RunBatch.created_at.desc()).first()

        if not batch:
            # Create and immediately execute batch synchronously for comparison
            batch = RunBatch(
                id=str(uuid.uuid4()),
                task_id=payload.task_id,
                agent_config_id=cfg_id,
                n_runs=payload.n_runs_per_config,
                concurrency_limit=3,
                status="pending",
                created_at=datetime.now(timezone.utc)
            )
            db.add(batch)
            db.commit()
            db.refresh(batch)
            await batch_runner.execute_batch(batch.id)

        batch_ids.append(batch.id)

    comparison = comparison_service.build_comparison(
        db=db,
        task_id=payload.task_id,
        batch_ids=batch_ids,
        comparison_name=payload.name or f"Comparison: {task.name}"
    )

    return comparison
