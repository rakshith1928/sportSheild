from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.rag_engine import explain_violation, query_rag

router = APIRouter()

@router.post("/violation")
async def explain_violation_endpoint(violation: dict):
    """
    Use RAG + Groq LLM to explain a detected violation
    and recommend legal actions
    """
    if not violation:
        raise HTTPException(
            status_code=400,
            detail="Violation data is required"
        )

    required_fields = ["image_url", "page_url", "clip_similarity"]
    for field in required_fields:
        if field not in violation:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )

    # Validate similarity score range
    similarity = violation.get("clip_similarity")
    if not isinstance(similarity, (int, float)) or not (0 <= similarity <= 1):
        raise HTTPException(
            status_code=400,
            detail="clip_similarity must be a number between 0 and 1"
        )

    try:
        result = explain_violation(violation)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "violation_url": violation.get("page_url"),
                "asset_id": violation.get("asset_id"),
                "confidence": result["confidence"],
                "severity": result["severity"],
                "explanation": result["explanation"],
                "legal_context": result["legal_context"],
                "recommended_action": result["recommended_action"]
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Explanation failed: {str(e)}"
        )


@router.post("/search-laws")
async def search_legal_knowledge(query: str, law: str = None):
    """
    Search the legal knowledge base directly.
    Optionally filter by law type: dmca, india_copyright, sports_rights
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    results = query_rag(query, law_filter=law)

    return {
        "query": query,
        "law_filter": law,
        "results_found": len(results),
        "legal_context": results
    }


@router.post("/batch")
async def explain_batch(violations: list):
    """
    Explain multiple violations at once.
    Returns explanations sorted by confidence descending.
    """
    if not violations:
        raise HTTPException(
            status_code=400,
            detail="violations list is required"
        )

    if len(violations) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 violations per batch"
        )

    results = []
    errors = []

    for i, violation in enumerate(violations):
        try:
            result = explain_violation(violation)
            results.append({
                "violation_url": violation.get("page_url"),
                "asset_id": violation.get("asset_id"),
                "confidence": result["confidence"],
                "severity": result["severity"],
                "explanation": result["explanation"],
                "recommended_action": result["recommended_action"]
            })
        except Exception as e:
            errors.append({
                "index": i,
                "url": violation.get("page_url", "unknown"),
                "error": str(e)
            })

    # Sort by confidence descending
    results = sorted(results, key=lambda x: x["confidence"], reverse=True)

    return {
        "success": True,
        "total_explained": len(results),
        "total_errors": len(errors),
        "results": results,
        "errors": errors
    }