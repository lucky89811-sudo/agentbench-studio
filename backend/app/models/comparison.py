import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    batch_ids = Column(JSON, nullable=False, default=list)  # list of batch UUIDs
    metrics_matrix = Column(JSON, nullable=False, default=dict)
    statistical_confidence = Column(JSON, nullable=False, default=dict)  # z_score, p_value, is_significant
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    task = relationship("Task", back_populates="comparisons")
