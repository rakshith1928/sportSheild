from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from services.report_generator import generate_report
from services.rag_engine import explain_violation
from services.database import insert_report as db_insert_report, get_reports as db_get_reports
from services.vector_store import get_asset_by_id
from services.job_store import create_job, update_job, get_job
from typing import cast
import logging
import uuid
import os

logger = logging.getLogger(__name__)

router = APIRouter()
REPORTS_DIR = "reports"


class Violation(BaseModel):
    page_url: str
    clip_similarity: float
    is_likely_copy: bool
    detected_at: str


class ReportRequest(BaseModel):
    asset_id: str
    violations: list[Violation]


def _process_report_background(job_id: str, request: ReportRequest, asset: dict):
    """Background worker function for RAG enrichment and PDF generation."""
    try:
        update_job(job_id, {"status": "processing"})
        os.makedirs(REPORTS_DIR, exist_ok=True)

        enriched_violations = []
        for v in request.violations:
            v_dict = v.model_dump()
            analysis = explain_violation(v_dict)
            enriched_violations.append({
                **v_dict,
                "severity": analysis.get("severity"),
                "confidence": round(v_dict.get("clip_similarity", 0) * 100, 2),
                "explanation": analysis.get("explanation"),
                "recommended_action": analysis.get("recommended_action"),
            })

        report_id = str(uuid.uuid4())[:8].upper()

        file_path = generate_report(
            asset=asset,
            violations=cast(list[dict], enriched_violations),
            report_id=report_id,
            output_dir=REPORTS_DIR,
        )

        try:
            db_insert_report({
                "report_id": report_id,
                "asset_id": request.asset_id,
                "violations_analyzed": len(enriched_violations),
                "file_path": file_path,
                "download_url": f"/report/download/{report_id}",
            })
        except Exception as db_err:
            logger.warning(f"Supabase report insert failed (non-fatal): {db_err}")

        update_job(job_id, {
            "status": "done",
            "report_id": report_id,
            "download_url": f"/report/download/{report_id}",
            "violations_analyzed": len(enriched_violations),
        })

    except Exception as e:
        logger.error(f"Background report generation failed for job {job_id}: {e}")
        update_job(job_id, {
            "status": "failed",
            "error": str(e),
        })


@router.post("/generate")
async def generate_violation_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """Enqueue AI-powered PDF report compilation in a background task (non-blocking)."""

    # Validate asset exists in pgvector
    try:
        asset = get_asset_by_id(request.asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Asset error: {str(e)}")

    job_id = str(uuid.uuid4())[:8].upper()
    create_job(job_id)

    background_tasks.add_task(
        _process_report_background,
        job_id=job_id,
        request=request,
        asset=cast(dict, asset),
    )

    return {
        "success": True,
        "job_id": job_id,
        "status": "queued",
        "message": "Report generation enqueued successfully"
    }


@router.get("/status/{job_id}")
async def get_report_job_status(job_id: str):
    """Query current status of a background report compilation job."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """Download a generated PDF report"""
    file_path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"sportshield_report_{report_id}.pdf",
    )


@router.get("/list")
async def list_reports(limit: int = 50, offset: int = 0):
    """List all generated reports with pagination"""
    try:
        return db_get_reports(limit=limit, offset=offset)
    except Exception:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".pdf")]
        files_sorted = sorted(files, reverse=True)
        paginated_files = files_sorted[offset:offset+limit]
        return {
            "total": len(files),
            "reports": [
                {
                    "report_id": f.replace(".pdf", ""),
                    "download_url": f"/report/download/{f.replace('.pdf', '')}",
                    "filename": f,
                }
                for f in paginated_files
            ]
        }