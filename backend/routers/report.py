from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from services.report_generator import generate_report
from services.rag_engine import explain_violation  #RAG integration
from services.database import insert_report as db_insert_report, get_reports as db_get_reports
import chromadb
import uuid
import os

router = APIRouter()
REPORTS_DIR = "reports"

# ✅ Initialize DB ONCE (performance fix)
chroma_client = chromadb.PersistentClient(
    path=os.getenv("CHROMA_DB_PATH", "./chroma_db")
)
collection = chroma_client.get_or_create_collection("sports_assets")


# ✅ Structured validation
class Violation(BaseModel):
    page_url: str
    clip_similarity: float
    is_likely_copy: bool
    detected_at: str


class ReportRequest(BaseModel):
    asset_id: str
    violations: list[Violation]


@router.post("/generate")
async def generate_violation_report(request: ReportRequest):
    """Generate AI-powered PDF report for an asset"""

    # Validate asset exists
    try:
        result = collection.get(ids=[request.asset_id])
        if not result["ids"]:
            raise HTTPException(status_code=404, detail="Asset not found")
        asset = result["metadatas"][0]
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Asset error: {str(e)}")

    # Ensure reports directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)

    try:
        enriched_violations = []

        # 🔥 RAG + LLM enrichment
        for v in request.violations:
            v_dict = v.dict()

            analysis = explain_violation(v_dict)

            enriched_violations.append({
                **v_dict,
                "severity": analysis.get("severity"),
                "confidence": round(v_dict.get("clip_similarity", 0) * 100, 2),
                "explanation": analysis.get("explanation"),
                "recommended_action": analysis.get("recommended_action")
            })

        # Generate report
        report_id = str(uuid.uuid4())[:8].upper()

        file_path = generate_report(
            asset=asset,
            violations=enriched_violations,  # ✅ FIXED
            report_id=report_id,
            output_dir=REPORTS_DIR
        )

        # Store report metadata in Supabase
        try:
            db_insert_report({
                "report_id": report_id,
                "asset_id": request.asset_id,
                "violations_analyzed": len(enriched_violations),
                "file_path": file_path,
                "download_url": f"/report/download/{report_id}",
            })
        except Exception as db_err:
            print(f"Supabase report insert failed (non-fatal): {db_err}")

        return {
            "success": True,
            "report_id": report_id,
            "download_url": f"/report/download/{report_id}",
            "violations_analyzed": len(enriched_violations)
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
    try:
        reports = db_get_reports()
        return {"total": len(reports), "reports": reports}
    except Exception:
        # Fallback to filesystem if Supabase is down
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