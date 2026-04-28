from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from services.report_generator import generate_report
from services.fingerprint import get_all_assets
import chromadb
import uuid
import os

router = APIRouter()

REPORTS_DIR = "reports"


class ReportRequest(BaseModel):
    asset_id: str
    violations: list


@router.post("/generate")
async def generate_violation_report(request: ReportRequest):
    """Generate a PDF report for an asset and its violations"""

    # Validate asset exists
    chroma_client = chromadb.PersistentClient(
        path=os.getenv("CHROMA_DB_PATH", "./chroma_db")
    )
    collection = chroma_client.get_or_create_collection("sports_assets")

    try:
        result = collection.get(ids=[request.asset_id])
        if not result["ids"]:
            raise HTTPException(status_code=404, detail="Asset not found")
        asset = result["metadatas"][0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Asset not found: {str(e)}")

    # Generate report
    try:
        report_id = str(uuid.uuid4())[:8].upper()
        file_path = generate_report(
            asset=asset,
            violations=request.violations,
            report_id=report_id,
            output_dir=REPORTS_DIR
        )

        return {
            "success": True,
            "report_id": report_id,
            "download_url": f"/report/download/{report_id}",
            "message": f"Report generated with {len(request.violations)} violations"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )


@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """Download a generated PDF report"""

    file_path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Report {report_id} not found"
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"sportshield_report_{report_id}.pdf"
    )


@router.get("/list")
async def list_reports():
    """List all generated reports"""

    os.makedirs(REPORTS_DIR, exist_ok=True)
    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".pdf")]

    return {
        "total": len(files),
        "reports": [
            {
                "report_id": f.replace(".pdf", ""),
                "download_url": f"/report/download/{f.replace('.pdf', '')}",
                "filename": f
            }
            for f in sorted(files, reverse=True)
        ]
    }