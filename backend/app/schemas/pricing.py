from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class PricingModelBase(BaseModel):
    model_name: str
    provider: str
    input_price_per_m: float = Field(..., ge=0.0)
    output_price_per_m: float = Field(..., ge=0.0)

class PricingModelCreate(PricingModelBase):
    pass

class PricingModelUpdate(BaseModel):
    input_price_per_m: float = Field(..., ge=0.0)
    output_price_per_m: float = Field(..., ge=0.0)

class PricingModelRead(PricingModelBase):
    id: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
