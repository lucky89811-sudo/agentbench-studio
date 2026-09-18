import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, JSON, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Run(Base):
    __tablename__ = "runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("run_batches.id"), nullable=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    agent_config_id = Column(String(36), ForeignKey("agent_configs.id"), nullable=False)
    run_index = Column(Integer, nullable=False, default=1)
    status = Column(String(32), nullable=False, default="pending")  # pending, running, completed, failed
    full_transcript = Column(JSON, nullable=False, default=list)  # list of step dicts
    final_output = Column(Text, nullable=False, default="")
    latency_ms = Column(Float, nullable=False, default=0.0)
    time_to_first_token_ms = Column(Float, nullable=False, default=0.0)
    token_usage = Column(JSON, nullable=False, default=lambda: {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
    cost_usd = Column(Float, nullable=False, default=0.0)
    error_trace = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    batch = relationship("RunBatch", back_populates="runs")
    task = relationship("Task", back_populates="runs")
    agent_config = relationship("AgentConfig", back_populates="runs")
    evaluation = relationship("Evaluation", back_populates="run", uselist=False, cascade="all, delete-orphan")
