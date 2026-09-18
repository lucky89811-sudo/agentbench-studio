from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from app.db.session import get_db
from app.models.agent_config import AgentConfig
from app.schemas.agent_config import AgentConfigCreate, AgentConfigUpdate, AgentConfigRead

router = APIRouter(prefix="/agent-configs", tags=["Agent Configs"])

@router.get("", response_model=list[AgentConfigRead])
def list_agent_configs(db: Session = Depends(get_db)):
    return db.query(AgentConfig).order_by(AgentConfig.created_at.desc()).all()

@router.get("/{config_id}", response_model=AgentConfigRead)
def get_agent_config(config_id: str, db: Session = Depends(get_db)):
    cfg = db.query(AgentConfig).filter(AgentConfig.id == config_id).first()
    if not cfg:
        raise HTTPException(status_code=404, detail="Agent Config not found")
    return cfg

@router.post("", response_model=AgentConfigRead)
def create_agent_config(payload: AgentConfigCreate, db: Session = Depends(get_db)):
    cfg = AgentConfig(
        id=str(uuid.uuid4()),
        **payload.model_dump()
    )
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg

@router.put("/{config_id}", response_model=AgentConfigRead)
def update_agent_config(config_id: str, payload: AgentConfigUpdate, db: Session = Depends(get_db)):
    cfg = db.query(AgentConfig).filter(AgentConfig.id == config_id).first()
    if not cfg:
        raise HTTPException(status_code=404, detail="Agent Config not found")
    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(cfg, k, v)
    db.commit()
    db.refresh(cfg)
    return cfg

@router.delete("/{config_id}")
def delete_agent_config(config_id: str, db: Session = Depends(get_db)):
    cfg = db.query(AgentConfig).filter(AgentConfig.id == config_id).first()
    if not cfg:
        raise HTTPException(status_code=404, detail="Agent Config not found")
    db.delete(cfg)
    db.commit()
    return {"message": "Agent Config deleted successfully"}
