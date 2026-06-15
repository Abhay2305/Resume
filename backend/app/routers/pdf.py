from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
import io
from ..schemas import TokenData
from ..auth import get_current_user
from ..models import User
from ..services.pdf_service import PDFExportService
from pydantic import BaseModel

class PDFExportRequest(BaseModel):
    html_content: str
    filename: str = "resume.pdf"

router = APIRouter(prefix="/pdf", tags=["PDF Export"])

@router.post("/export")
def export_pdf(req: PDFExportRequest, current_user: User = Depends(get_current_user)):
    """
    Exports a high-fidelity PDF from the compiled HTML/CSS template sent by the client.
    """
    if not req.html_content:
        raise HTTPException(status_code=400, detail="HTML content is required for export.")
        
    try:
        pdf_bytes = PDFExportService.html_to_pdf(req.html_content)
        
        # Return streaming file response
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={req.filename}"
            }
        )
    except Exception as e:
        print(f"Error serving PDF download: {e}")
        raise HTTPException(status_code=500, detail=f"PDF compilation failed: {e}")
