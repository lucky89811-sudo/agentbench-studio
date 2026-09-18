import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime
from app.db.base import Base

class PricingModel(Base):
    __tablename__ = "pricing_models"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name = Column(String(128), unique=True, nullable=False)
    provider = Column(String(64), nullable=False, default="openai")
    input_price_per_m = Column(Float, nullable=False, default=2.50)   # USD per 1M tokens
    output_price_per_m = Column(Float, nullable=False, default=10.00) # USD per 1M tokens
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
