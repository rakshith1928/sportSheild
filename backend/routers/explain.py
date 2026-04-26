from fastapi import APIRouter

router = APIRouter()

@router.post("/violation")
async def explain_violation():
    """RAG legal explanation - Phase 4"""
    return {"message": "Coming in Phase 4"}