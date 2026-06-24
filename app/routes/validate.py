from fastapi import APIRouter, HTTPException
from app.models import ValidationRequest, ValidationResponse
from app.validator import validate_table

# ---------------------------------------------------------------------------
# Validation Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.post(
    "/validate",
    response_model=ValidationResponse,
    tags=["Validation"],
    summary="Run a validation job against a dataset",
    description="""
    Accepts a table name, a list of data records, and a set of column rules.
    Runs the validation engine and returns a structured result per column
    along with an overall job status.
    
    Use this endpoint to validate data quality post-release — checking for
    nulls, duplicates, and out-of-range values across business-critical columns.
    """
)
def run_validation(request: ValidationRequest) -> ValidationResponse:
    """
    Core validation endpoint.
    
    - Accepts: ValidationRequest (table_name, data, rules)
    - Returns: ValidationResponse (job_id, status, column_results, summary)
    - Raises: 400 if request payload is invalid
              500 if an unexpected error occurs during validation
    """
    try:
        result = validate_table(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation engine error: {str(e)}")


@router.get(
    "/validate/health",
    tags=["Validation"],
    summary="Check validation engine status"
)
def validation_engine_health():
    """
    Confirms the validation engine is loaded and ready to accept jobs.
    """
    return {
        "engine": "ready",
        "supported_checks": ["not_null", "unique", "min_value", "max_value"]
    }