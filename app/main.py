from fastapi import FastAPI
from app.routes import health, validate

# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="FastAPI Data Validator",
    description="""
    A production-style REST API for automated data validation.
    
    Built to demonstrate:
    - FastAPI REST API design
    - Pydantic v2 structured data models
    - Separation of concerns (routes → business logic → models)
    - Production-grade error handling
    - Auto-generated Swagger documentation
    
    Inspired by real-world regression testing at enterprise scale —
    validating business-critical tables post-release across 100+ 
    production datasets.
    """,
    version="1.0.0",
    contact={
        "name": "Anurag Gupta",
        "url": "https://github.com/anuraggupta",
    },
)

# ---------------------------------------------------------------------------
# Register Routers
# ---------------------------------------------------------------------------

app.include_router(health.router, prefix="/api/v1")
app.include_router(validate.router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint — confirms API is live and points to docs.
    """
    return {
        "message": "FastAPI Data Validator is running",
        "docs": "/docs",
        "health": "/api/v1/health",
        "validate": "/api/v1/validate"
    }