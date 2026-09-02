"""
Validation Report JSON Formatter for MPLADS Ingestion and Quality Audits.
Generates structured JSON validation reports conforming to backend API contracts.
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime

try:
    from .schemas import ValidationSummary, ValidationIssue
except (ImportError, ValueError):
    from schemas import ValidationSummary, ValidationIssue



RULE_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    "DQ_MISSING_PRIMARY_KEY": {
        "name": "Missing Primary Key",
        "category": "DATA_QUALITY_ISSUE",
        "description": "The mandatory primary key (work_id) is missing or blank.",
    },
    "DQ_DUPLICATE_WORK_ID": {
        "name": "Duplicate Work ID",
        "category": "DATA_QUALITY_ISSUE",
        "description": "A work_id appears multiple times within the batch or database.",
    },
    "DQ_INVALID_CATEGORY": {
        "name": "Unstandardized Work Category",
        "category": "DATA_QUALITY_ISSUE",
        "description": "The work category does not match one of the 8 standard peer-group categories.",
    },
    "DQ_INVALID_STATE_DISTRICT": {
        "name": "State-District Hierarchy Violation",
        "category": "DATA_QUALITY_ISSUE",
        "description": "The specified district does not exist under the declared state.",
    },
    "DQ_NEGATIVE_AMOUNT": {
        "name": "Negative Financial Value",
        "category": "DATA_QUALITY_ISSUE",
        "description": "Financial amount fields (estimate, sanction, payments, expenditure) must be >= 0.",
    },
    "RULE_PAYMENTS_EXCEED_SANCTION": {
        "name": "Disbursements Exceed Sanctioned Budget",
        "category": "COMPLIANCE_RULE_VIOLATION",
        "description": "Total released payments exceed the administrative sanctioned limit for this work.",
    },
    "DQ_PROGRESS_OUT_OF_RANGE": {
        "name": "Physical Progress Out of Range",
        "category": "DATA_QUALITY_ISSUE",
        "description": "Physical progress percentage is outside the valid range of 0.0% to 100.0%.",
    },
    "DQ_INVALID_DATE_ORDER": {
        "name": "Chronological Inversion",
        "category": "DATA_QUALITY_ISSUE",
        "description": "Dates do not follow logical progression (recommendation <= sanction <= work order <= completion).",
    },
    "DQ_FUTURE_DATE": {
        "name": "Future Date Record",
        "category": "DATA_QUALITY_ISSUE",
        "description": "Recorded date timestamp is ahead of the current evaluation date.",
    },
    "DQ_MALFORMED_DATE": {
        "name": "Malformed Date String",
        "category": "DATA_QUALITY_ISSUE",
        "description": "Date format cannot be parsed into standard ISO YYYY-MM-DD format.",
    },
    "RULE_MISSING_COMPLETION_EVIDENCE": {
        "name": "Missing Completion Evidence",
        "category": "COMPLIANCE_RULE_VIOLATION",
        "description": "Work is marked completed or 100% progressed but lacks completion date certificate.",
    },
    "DQ_COORDINATES_OUT_OF_BOUNDS": {
        "name": "Geographic Coordinates Out of Bounds",
        "category": "DATA_QUALITY_ISSUE",
        "description": "GPS coordinates are missing or lie outside Indian territorial boundaries.",
    },
}


class ValidationReportFormatter:
    """
    Builds clean, structured JSON reports for frontend ingestion modals and backend audit logs.
    """

    @staticmethod
    def build_report(
        summary: ValidationSummary,
        issues: List[ValidationIssue],
        batch_id: Optional[str] = None,
        source_filename: Optional[str] = None,
        max_sample_issues: int = 500,
    ) -> Dict[str, Any]:
        """
        Creates a JSON-serializable dictionary report.
        """
        formatted_issues = [iss.to_dict() for iss in issues[:max_sample_issues]]

        # Build rule breakdown with human-readable labels
        rule_breakdown: List[Dict[str, Any]] = []
        for rule_code, count in summary.issues_by_rule.items():
            meta = RULE_DESCRIPTIONS.get(rule_code, {"name": rule_code, "category": "DATA_QUALITY_ISSUE", "description": ""})
            rule_breakdown.append({
                "rule_code": rule_code,
                "rule_name": meta["name"],
                "category": meta["category"],
                "count": count,
                "description": meta["description"],
            })

        rule_breakdown.sort(key=lambda x: x["count"], reverse=True)

        return {
            "validation_report_version": "1.0.0",
            "synthetic_demo_data": True,
            "metadata": {
                "batch_id": batch_id or f"BATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "source_filename": source_filename or "mplads_upload.csv",
                "generated_at": summary.validation_timestamp,
                "status": "PASSED" if summary.invalid_records == 0 else "FAILED_VALIDATION",
            },
            "summary": {
                "total_records": summary.total_records,
                "valid_records": summary.valid_records,
                "invalid_records": summary.invalid_records,
                "total_issues": summary.total_issues,
                "data_quality_score_pct": summary.data_quality_score_pct,
                "issues_by_severity": summary.issues_by_severity,
                "issues_by_category": summary.issues_by_category,
            },
            "rule_breakdown": rule_breakdown,
            "issues_sample": formatted_issues,
            "total_issues_sampled": len(formatted_issues),
            "total_issues_omitted": max(0, len(issues) - max_sample_issues),
        }

    @staticmethod
    def export_json(report: Dict[str, Any], output_path: str) -> None:
        with open(output_path, mode="w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
