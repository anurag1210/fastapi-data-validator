from fastapi import APIRouter
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Health Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.
    
    Used by load balancers, monitoring tools, and deployment pipelines
    to verify the API is running and responsive.
    
    Returns:
    - status: always 'healthy' if the service is up
    - timestamp: current UTC time
    - version: API version
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }