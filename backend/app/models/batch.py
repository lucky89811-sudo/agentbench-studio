import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, JSON, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class RunBatch(Base):
    __tablename__ = "run_batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    agent_config_id = Column(String(36), ForeignKey("agent_configs.id"), nullable=False)
    n_runs = Column(Integer, nullable=False, default=5)
    concurrency_limit = Column(Integer, nullable=False, default=3)
    status = Column(String(32), nullable=False, default="pending")  # pending, running, completed, failed, cancelled
    completed_runs_count = Column(Integer, nullable=False, default=0)
    failed_runs_count = Column(Integer, nullable=False, default=0)
    summary_metrics = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    task = relationship("Task", back_populates="batches")
    agent_config = relationship("AgentConfig", back_populates="batches")
    runs = relationship("Run", back_populates="batch", cascade="all, delete-orphan", order_by="Run.run_index")
