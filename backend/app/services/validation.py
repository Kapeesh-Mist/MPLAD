"""
Backend Validation Service.
Provides high-level validation APIs for work records, payment batches, and inspection audits.
"""

from typing import Dict, List, Any, Optional
import os
import sys

# Ensure data package is importable
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from data.synthetic_generator.validator import MPLADSDataValidator, ValidationRuleCode
from data.synthetic_generator.report_formatter import ValidationReportFormatter


class ValidationService:
    """
    Backend service exposing validation functions for business logic and API endpoints.
    """

    def __init__(self):
        self.validator = MPLADSDataValidator()

    def validate_records(
        self,
        records: List[Dict[str, Any]],
        source_name: str = "api_batch"
    ) -> Dict[str, Any]:
        """
        Validates a list of work record dicts and returns a JSON-serializable report.
        """
        summary, issues = self.validator.validate_dataset(records)
        return ValidationReportFormatter.build_report(
            summary=summary,
            issues=issues,
            source_filename=source_name,
        )

    def validate_single_record(
        self,
        record: Dict[str, Any],
        row_number: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Validates a single record and returns any identified issues.
        """
        seen: set = set()
        issues = self.validator.validate_work_record(record, row_number, seen)
        return [iss.to_dict() for iss in issues]
