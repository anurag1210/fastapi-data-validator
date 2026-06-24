from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ValidationStatus(str, Enum):
    """
    Represents the outcome of a validation check.
    - PASSED: all rules met
    - FAILED: one or more critical rules violated
    - WARNING: minor issues detected but not critical
    """
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class ColumnRule(BaseModel):
    """
    Defines the validation rules to apply against a single column.
    Each rule is optional — only the rules explicitly set will be enforced.
    
    Example:
        {
            "column_name": "customer_id",
            "not_null": true,
            "unique": true,
            "min_value": 1,
            "max_value": 999999
        }
    """
    column_name: str = Field(..., description="Name of the column to validate")
    not_null: bool = Field(default=True, description="Column must not contain nulls")
    unique: bool = Field(default=False, description="Column values must be unique")
    min_value: Optional[float] = Field(default=None, description="Minimum allowed value")
    max_value: Optional[float] = Field(default=None, description="Maximum allowed value")


class ValidationRequest(BaseModel):
    """
    The inbound payload for a validation job.
    
    Contains:
    - table_name: identifies the table being validated (e.g. 'customer_accounts')
    - data: the actual records to validate, passed as a list of dicts
    - rules: the set of ColumnRule objects defining what to check per column
    
    Example:
        {
            "table_name": "customer_accounts",
            "data": [{"customer_id": 1, "email": "a@b.com"}, ...],
            "rules": [{"column_name": "customer_id", "not_null": true, "unique": true}]
        }
    """
    table_name: str = Field(..., description="Name of the table being validated")
    data: list[dict] = Field(..., description="List of records to validate")
    rules: list[ColumnRule] = Field(..., description="Validation rules to apply")


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class ColumnValidationResult(BaseModel):
    """
    Captures the validation outcome for a single column.
    
    Contains:
    - column_name: the column that was checked
    - status: PASSED / FAILED / WARNING
    - null_count: number of null values found
    - duplicate_count: number of duplicate values found (if unique rule applied)
    - out_of_range_count: number of values outside min/max bounds
    - message: human-readable summary of the result
    """
    column_name: str
    status: ValidationStatus
    null_count: int = 0
    duplicate_count: int = 0
    out_of_range_count: int = 0
    message: str


class ValidationResponse(BaseModel):
    """
    The full validation response returned to the API consumer after a job completes.
    
    Contains:
    - job_id: unique identifier for this validation run (UUID)
    - table_name: the table that was validated
    - status: overall PASSED / FAILED / WARNING across all columns
    - total_records: number of records that were validated
    - validated_at: timestamp of when the validation ran
    - column_results: list of ColumnValidationResult — one per rule applied
    - summary: human-readable overall summary message
    
    This model is serialised directly to JSON in the API response.
    """
    job_id: str
    table_name: str
    status: ValidationStatus
    total_records: int
    validated_at: datetime
    column_results: list[ColumnValidationResult]
    summary: str