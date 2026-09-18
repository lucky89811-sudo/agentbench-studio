import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False, default="tool-use")  # research, coding, tool-use, citation
    prompt_template = Column(Text, nullable=False)
    expected_output_schema = Column(JSON, nullable=True)
    success_criteria = Column(JSON, nullable=False, default=dict)  # structured rules + rubric
    required_tools = Column(JSON, nullable=False, default=list)
    budget_constraints = Column(JSON, nullable=True, default=dict)  # max_latency_ms, max_cost_usd
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    runs = relationship("Run", back_populates="task", cascade="all, delete-orphan")
    batches = relationship("RunBatch", back_populates="task", cascade="all, delete-orphan")
    comparisons = relationship("Comparison", back_populates="task", cascade="all, delete-orphan")
