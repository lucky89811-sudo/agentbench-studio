import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, JSON, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("runs.id"), nullable=False, unique=True)
    
    # Headline scores
    overall_passed = Column(Boolean, nullable=False, default=False)
    overall_score = Column(Float, nullable=False, default=0.0)  # 0 to 100

    # Evaluator a: Task Completion
    completion_rate = Column(Boolean, nullable=False, default=False)
    completion_score = Column(Float, nullable=False, default=0.0)
    completion_details = Column(JSON, nullable=False, default=dict)

    # Evaluator b: Tool-Call Accuracy
    tool_call_accuracy = Column(Float, nullable=False, default=100.0)
    tool_error_count = Column(Integer, nullable=False, default=0)
    unnecessary_tool_calls = Column(Integer, nullable=False, default=0)
    ignored_tool_errors = Column(Integer, nullable=False, default=0)
    tool_details = Column(JSON, nullable=False, default=dict)

    # Evaluator c: Citation Correctness
    citation_precision = Column(Float, nullable=False, default=100.0)
    uncited_claims_count = Column(Integer, nullable=False, default=0)
    broken_link_count = Column(Integer, nullable=False, default=0)
    citation_details = Column(JSON, nullable=False, default=dict)

    # Evaluator d: Hallucination Detector
    hallucination_rate = Column(Float, nullable=False, default=0.0)
    phantom_tool_use_count = Column(Integer, nullable=False, default=0)
    hallucination_details = Column(JSON, nullable=False, default=dict)

    # Evaluator e: Latency & Cost Breakdown
    latency_details = Column(JSON, nullable=False, default=dict)
    cost_details = Column(JSON, nullable=False, default=dict)

    # Raw results from each evaluator
    raw_evaluator_results = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    run = relationship("Run", back_populates="evaluation")
