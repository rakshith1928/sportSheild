from fastapi import APIRouter, Depends
from services.database import get_dashboard_stats
from dependencies import get_current_user

router = APIRouter()

@router.get("/stats")
async def get_stats(user = Depends(get_current_user)):
    """Get high-level statistics for the main dashboard"""
    # Pass the authenticated user's ID to the database function
    stats = get_dashboard_stats(user_id=user.id)
    return stats
