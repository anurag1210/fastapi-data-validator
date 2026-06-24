import uuid
from datetime import datetime, timezone
from app.models import (
    ValidationRequest,
    ValidationResponse,
    ColumnValidationResult,
    ValidationStatus,
)


# ---------------------------------------------------------------------------
# Core Validation Engine
# ---------------------------------------------------------------------------

def validate_table(request: ValidationRequest) -> ValidationResponse:
    """
    Core validation engine. Accepts a ValidationRequest and applies
    each ColumnRule against the provided dataset.

    For each column rule it checks:
    - Null values (if not_null=True)
    - Duplicate values (if unique=True)
    - Out of range values (if min_value or max_value specified)

    Returns a ValidationResponse with per-column results and an
    overall status reflecting the worst outcome across all columns.
    """
    column_results = []

    for rule in request.rules:
        # Extract values for this column from all records
        values = [
            record.get(rule.column_name)
            for record in request.data
        ]

        null_count = 0
        duplicate_count = 0
        out_of_range_count = 0
        issues = []

        # ---------------------------------------------------------------
        # Null check
        # ---------------------------------------------------------------
        if rule.not_null:
            null_count = sum(1 for v in values if v is None)
            if null_count > 0:
                issues.append(f"{null_count} null value(s) found")

        # ---------------------------------------------------------------
        # Uniqueness check
        # ---------------------------------------------------------------
        if rule.unique:
            non_null_values = [v for v in values if v is not None]
            duplicate_count = len(non_null_values) - len(set(non_null_values))
            if duplicate_count > 0:
                issues.append(f"{duplicate_count} duplicate value(s) found")

        # ---------------------------------------------------------------
        # Range check
        # ---------------------------------------------------------------
        if rule.min_value is not None or rule.max_value is not None:
            for v in values:
                if v is None:
                    continue
                try:
                    numeric_v = float(v)
                    if rule.min_value is not None and numeric_v < rule.min_value:
                        out_of_range_count += 1
                    elif rule.max_value is not None and numeric_v > rule.max_value:
                        out_of_range_count += 1
                except (ValueError, TypeError):
                    issues.append(f"Non-numeric value found in column '{rule.column_name}'")
                    break

            if out_of_range_count > 0:
                issues.append(f"{out_of_range_count} value(s) out of range")

        # ---------------------------------------------------------------
        # Determine column status
        # ---------------------------------------------------------------
        if null_count > 0 or duplicate_count > 0 or out_of_range_count > 0:
            status = ValidationStatus.FAILED
            message = f"Column '{rule.column_name}' failed: {', '.join(issues)}"
        else:
            status = ValidationStatus.PASSED
            message = f"Column '{rule.column_name}' passed all validation rules"

        column_results.append(
            ColumnValidationResult(
                column_name=rule.column_name,
                status=status,
                null_count=null_count,
                duplicate_count=duplicate_count,
                out_of_range_count=out_of_range_count,
                message=message,
            )
        )

    # ---------------------------------------------------------------
    # Determine overall job status
    # ---------------------------------------------------------------
    if any(r.status == ValidationStatus.FAILED for r in column_results):
        overall_status = ValidationStatus.FAILED
        summary = f"Validation FAILED for table '{request.table_name}' — one or more columns did not meet the required rules."
    else:
        overall_status = ValidationStatus.PASSED
        summary = f"Validation PASSED for table '{request.table_name}' — all {len(request.rules)} column rule(s) met across {len(request.data)} record(s)."

    return ValidationResponse(
        job_id=str(uuid.uuid4()),
        table_name=request.table_name,
        status=overall_status,
        total_records=len(request.data),
        validated_at=datetime.now(timezone.utc),
        column_results=column_results,
        summary=summary,
    )