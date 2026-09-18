from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from app.db.session import get_db
from app.models.pricing import PricingModel
from app.schemas.pricing import PricingModelCreate, PricingModelUpdate, PricingModelRead

router = APIRouter(prefix="/pricing", tags=["Pricing Table"])

@router.get("", response_model=list[PricingModelRead])
def list_pricing_models(db: Session = Depends(get_db)):
    return db.query(PricingModel).order_by(PricingModel.model_name.asc()).all()

@router.post("", response_model=PricingModelRead)
def create_pricing_model(payload: PricingModelCreate, db: Session = Depends(get_db)):
    existing = db.query(PricingModel).filter(PricingModel.model_name == payload.model_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Pricing for model already exists")
    pm = PricingModel(
        id=str(uuid.uuid4()),
        **payload.model_dump()
    )
    db.add(pm)
    db.commit()
    db.refresh(pm)
    return pm

@router.put("/{pricing_id}", response_model=PricingModelRead)
def update_pricing_model(pricing_id: str, payload: PricingModelUpdate, db: Session = Depends(get_db)):
    pm = db.query(PricingModel).filter(PricingModel.id == pricing_id).first()
    if not pm:
        raise HTTPException(status_code=404, detail="Pricing model not found")
    pm.input_price_per_m = payload.input_price_per_m
    pm.output_price_per_m = payload.output_price_per_m
    db.commit()
    db.refresh(pm)
    return pm
