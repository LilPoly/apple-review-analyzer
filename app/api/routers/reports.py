import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response

from app.api.dependencies import get_pdf_report_service
from app.services.report.pdf_report_service import PdfReportService

router = APIRouter(prefix="/jobs", tags=["reports"])


@router.get("/{job_id}/report/pdf")
def get_pdf_report(
    job_id: uuid.UUID,
    service: Annotated[PdfReportService, Depends(get_pdf_report_service)],
) -> Response:
    try:
        pdf_bytes = service.generate(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report_{job_id}.pdf"'},
    )
