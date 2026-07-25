"""
SportShield AI — Background Job Store
In-memory dictionary to track background report compilation tasks.
"""

from typing import Dict, Any, Optional
import time

# Job structure:
# {
#    "status": "queued" | "processing" | "done" | "failed",
#    "created_at": float,
#    "report_id": Optional[str],
#    "download_url": Optional[str],
#    "violations_analyzed": Optional[int],
#    "error": Optional[str]
# }

_jobs: Dict[str, Dict[str, Any]] = {}

def create_job(job_id: str) -> Dict[str, Any]:
    """Initialize a new job in queued status."""
    job = {
        "job_id": job_id,
        "status": "queued",
        "created_at": time.time(),
        "report_id": None,
        "download_url": None,
        "violations_analyzed": None,
        "error": None
    }
    _jobs[job_id] = job
    return job

def update_job(job_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update job fields."""
    if job_id in _jobs:
        _jobs[job_id].update(updates)
        return _jobs[job_id]
    return None

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve job details by ID."""
    return _jobs.get(job_id)
