import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, JSON, Float, Integer, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

class AgentConfig(Base):
    __tablename__ = "agent_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    provider = Column(String(64), nullable=False, default="mock")  # openai, anthropic, gemini, generic, mock
    model = Column(String(128), nullable=False, default="gpt-4o")
    system_prompt = Column(Text, nullable=False, default="")
    prompt_version = Column(String(32), nullable=False, default="v1.0.0")
    temperature = Column(Float, nullable=False, default=0.0)
    tool_definitions = Column(JSON, nullable=False, default=list)  # tool schemas enabled for agent
    max_steps = Column(Integer, nullable=False, default=8)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    runs = relationship("Run", back_populates="agent_config", cascade="all, delete-orphan")
    batches = relationship("RunBatch", back_populates="agent_config", cascade="all, delete-orphan")
