from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.report_service import report_service
from app.services.pdf_service import pdf_generator

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/{batch_id}")
def get_evaluation_report(batch_id: str, db: Session = Depends(get_db)):
    report = report_service.generate_batch_report(db, batch_id)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    return report

@router.get("/{batch_id}/pdf")
def export_evaluation_report_pdf(batch_id: str, db: Session = Depends(get_db)):
    report = report_service.generate_batch_report(db, batch_id)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])

    pdf_buffer = pdf_generator.generate_pdf(report)
    filename = f"agentbench_report_{batch_id[:8]}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
