"""
Validation Engine for MPLADS Synthetic & Ingested Datasets.
Performs data quality checks, schema constraint verifications, and compliance rule evaluations.
Categorizes findings neutrally into DATA_QUALITY_ISSUE and COMPLIANCE_RULE_VIOLATION without defamatory assertions.
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
import re

try:
    from .constants import (
        CATEGORIES,
        STATE_DISTRICT_MASTER,
        INDIA_GEO_BOUNDS,
        STATUS_COMPLETED,
        STATUS_SANCTIONED,
        STATUS_WORK_ORDER,
        STATUS_IN_PROGRESS,
        STATUS_STALLED,
    )
    from .schemas import ValidationIssue, ValidationSummary
except (ImportError, ValueError):
    from constants import (
        CATEGORIES,
        STATE_DISTRICT_MASTER,
        INDIA_GEO_BOUNDS,
        STATUS_COMPLETED,
        STATUS_SANCTIONED,
        STATUS_WORK_ORDER,
        STATUS_IN_PROGRESS,
        STATUS_STALLED,
    )
    from schemas import ValidationIssue, ValidationSummary



class ValidationRuleCode:
    DQ_MISSING_PRIMARY_KEY = "DQ_MISSING_PRIMARY_KEY"
    DQ_INVALID_DATE_ORDER = "DQ_INVALID_DATE_ORDER"
    DQ_FUTURE_DATE = "DQ_FUTURE_DATE"
    DQ_MALFORMED_DATE = "DQ_MALFORMED_DATE"
    DQ_NEGATIVE_AMOUNT = "DQ_NEGATIVE_AMOUNT"
    RULE_PAYMENTS_EXCEED_SANCTION = "RULE_PAYMENTS_EXCEED_SANCTION"
    DQ_PROGRESS_OUT_OF_RANGE = "DQ_PROGRESS_OUT_OF_RANGE"
    RULE_MISSING_COMPLETION_EVIDENCE = "RULE_MISSING_COMPLETION_EVIDENCE"
    DQ_DUPLICATE_WORK_ID = "DQ_DUPLICATE_WORK_ID"
    DQ_INVALID_STATE_DISTRICT = "DQ_INVALID_STATE_DISTRICT"
    DQ_COORDINATES_OUT_OF_BOUNDS = "DQ_COORDINATES_OUT_OF_BOUNDS"
    DQ_INVALID_CATEGORY = "DQ_INVALID_CATEGORY"
    DQ_MISSING_AGENCY_LINK = "DQ_MISSING_AGENCY_LINK"


class MPLADSDataValidator:
    """
    Validates MPLADS dataset records against regulatory, geographic, and data quality constraints.
    """

    def __init__(self, reference_date: Optional[datetime] = None):
        # Default reference date for temporal sanity checks
        self.reference_date = reference_date or datetime(2026, 3, 1)

    def _parse_date(self, val: Any) -> Optional[datetime]:
        if not val or val == "" or str(val).lower() in ["none", "null", "nan", "nat"]:
            return None
        if isinstance(val, datetime):
            return val
        val_str = str(val).strip()
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(val_str, fmt)
            except ValueError:
                pass
        return "MALFORMED"  # Sentinel for unparseable date

    def validate_work_record(
        self,
        record: Dict[str, Any],
        row_number: int,
        seen_work_ids: Set[str]
    ) -> List[ValidationIssue]:
        """
        Validates a single work record dictionary.
        """
        issues: List[ValidationIssue] = []
        issue_count = 0

        def add_issue(
            field_name: str,
            cat: str,
            rule: str,
            sev: str,
            msg: str,
            invalid_val: Any,
            expected: str
        ):
            nonlocal issue_count
            issue_count += 1
            issues.append(
                ValidationIssue(
                    issue_id=f"ISSUE-ROW{row_number}-{issue_count}",
                    row_number=row_number,
                    work_id=record.get("work_id"),
                    field_name=field_name,
                    issue_category=cat,
                    rule_code=rule,
                    severity=sev,
                    message=msg,
                    invalid_value=str(invalid_val),
                    expected_condition=expected,
                )
            )

        work_id = str(record.get("work_id", "")).strip()

        # 1. Missing / Blank Work ID
        if not work_id or work_id.lower() in ["none", "null", "nan", ""]:
            add_issue(
                "work_id",
                "DATA_QUALITY_ISSUE",
                ValidationRuleCode.DQ_MISSING_PRIMARY_KEY,
                "CRITICAL",
                "Mandatory work_id primary key is missing or empty.",
                work_id,
                "Non-empty unique string identifier",
            )
        else:
            # 2. Duplicate Work ID check
            if work_id in seen_work_ids:
                add_issue(
                    "work_id",
                    "DATA_QUALITY_ISSUE",
                    ValidationRuleCode.DQ_DUPLICATE_WORK_ID,
                    "CRITICAL",
                    f"Duplicate work_id '{work_id}' detected in dataset upload.",
                    work_id,
                    "Unique identifier across entire dataset",
                )
            seen_work_ids.add(work_id)

        # 3. Category Check
        category = record.get("category")
        if not category or category not in CATEGORIES:
            add_issue(
                "category",
                "DATA_QUALITY_ISSUE",
                ValidationRuleCode.DQ_INVALID_CATEGORY,
                "ERROR",
                f"Work category '{category}' is invalid or unstandardized.",
                category,
                f"One of standard peer-group categories: {', '.join(CATEGORIES)}",
            )

        # 4. State / District Geographical Master Check
        state = record.get("state")
        district = record.get("district")
        if not state or state not in STATE_DISTRICT_MASTER:
            add_issue(
                "state",
                "DATA_QUALITY_ISSUE",
                ValidationRuleCode.DQ_INVALID_STATE_DISTRICT,
                "ERROR",
                f"State '{state}' is not found in master reference registry.",
                state,
                "Valid Indian state name in master list",
            )
        elif not district or district not in STATE_DISTRICT_MASTER[state]:
            add_issue(
                "district",
                "DATA_QUALITY_ISSUE",
                ValidationRuleCode.DQ_INVALID_STATE_DISTRICT,
                "ERROR",
                f"District '{district}' is not recognized under state '{state}'.",
                f"{state} -> {district}",
                f"Valid district belonging to {state}",
            )

        # 5. Financial Amounts: Non-negative and Cap Checks
        numeric_fields = ["estimate_amount", "sanctioned_amount", "cumulative_payments", "expenditure"]
        parsed_amounts: Dict[str, float] = {}
        for f in numeric_fields:
            raw_val = record.get(f)
            try:
                val_float = float(raw_val) if raw_val is not None and str(raw_val).strip() != "" else 0.0
                parsed_amounts[f] = val_float
                if val_float < 0:
                    add_issue(
                        f,
                        "DATA_QUALITY_ISSUE",
                        ValidationRuleCode.DQ_NEGATIVE_AMOUNT,
                        "ERROR",
                        f"Financial field '{f}' contains negative amount: Rs. {val_float:,.2f}.",
                        val_float,
                        "Amount >= 0.0",
                    )
            except (ValueError, TypeError):
                add_issue(
                    f,
                    "DATA_QUALITY_ISSUE",
                    ValidationRuleCode.DQ_NEGATIVE_AMOUNT,
                    "ERROR",
                    f"Financial field '{f}' contains non-numeric value: '{raw_val}'.",
                    raw_val,
                    "Numeric decimal value",
                )
                parsed_amounts[f] = 0.0

        # Payments vs Sanction cap check
        sanctioned = parsed_amounts.get("sanctioned_amount", 0.0)
        cumulative_pay = parsed_amounts.get("cumulative_payments", 0.0)
        status = record.get("status")

        if sanctioned > 0 and cumulative_pay > (sanctioned * 1.01):  # allow 1% rounding tolerance
            add_issue(
                "cumulative_payments",
                "COMPLIANCE_RULE_VIOLATION",
                ValidationRuleCode.RULE_PAYMENTS_EXCEED_SANCTION,
                "ERROR",
                f"Cumulative payments (Rs. {cumulative_pay:,.2f}) exceed sanctioned budget (Rs. {sanctioned:,.2f}).",
                cumulative_pay,
                f"Cumulative payments <= sanctioned amount (Rs. {sanctioned:,.2f})",
            )

        # 6. Physical Progress: 0 to 100%
        raw_progress = record.get("physical_progress_pct")
        try:
            progress_pct = float(raw_progress) if raw_progress is not None and str(raw_progress).strip() != "" else 0.0
            if progress_pct < 0.0 or progress_pct > 100.0:
                add_issue(
                    "physical_progress_pct",
                    "DATA_QUALITY_ISSUE",
                    ValidationRuleCode.DQ_PROGRESS_OUT_OF_RANGE,
                    "ERROR",
                    f"Physical progress {progress_pct}% is outside allowable 0.0% to 100.0% range.",
                    progress_pct,
                    "0.0 <= physical_progress_pct <= 100.0",
                )
        except (ValueError, TypeError):
            add_issue(
                "physical_progress_pct",
                "DATA_QUALITY_ISSUE",
                ValidationRuleCode.DQ_PROGRESS_OUT_OF_RANGE,
                "ERROR",
                f"Physical progress contains non-numeric value: '{raw_progress}'.",
                raw_progress,
                "Numeric value between 0.0 and 100.0",
            )
            progress_pct = 0.0

        # 7. Date Validation & Chronological Integrity
        historical_date_fields = [
            "recommendation_date",
            "sanction_date",
            "work_order_date",
            "commencement_date",
            "actual_completion_date",
        ]
        all_date_fields = historical_date_fields + ["target_completion_date"]
        parsed_dates: Dict[str, Optional[datetime]] = {}
        
        for df in all_date_fields:
            val = record.get(df)
            parsed = self._parse_date(val)
            if parsed == "MALFORMED":
                add_issue(
                    df,
                    "DATA_QUALITY_ISSUE",
                    ValidationRuleCode.DQ_MALFORMED_DATE,
                    "ERROR",
                    f"Date field '{df}' contains malformed date string '{val}'.",
                    val,
                    "Standard ISO date format (YYYY-MM-DD)",
                )
                parsed_dates[df] = None
            else:
                # Past/historical milestones should not be in the future
                if parsed and df in historical_date_fields and parsed > self.reference_date:
                    add_issue(
                        df,
                        "DATA_QUALITY_ISSUE",
                        ValidationRuleCode.DQ_FUTURE_DATE,
                        "WARNING",
                        f"Historical date field '{df}' ({parsed.strftime('%Y-%m-%d')}) is recorded after system evaluation date ({self.reference_date.strftime('%Y-%m-%d')}).",
                        parsed.strftime("%Y-%m-%d"),
                        f"Date <= {self.reference_date.strftime('%Y-%m-%d')}",
                    )
                parsed_dates[df] = parsed


        # Chronological order rules
        # rec <= sanction <= work_order <= commencement
        d_rec = parsed_dates.get("recommendation_date")
        d_sanc = parsed_dates.get("sanction_date")
        d_wo = parsed_dates.get("work_order_date")
        d_comm = parsed_dates.get("commencement_date")
        d_comp = parsed_dates.get("actual_completion_date")

        if d_rec and d_sanc and d_sanc < d_rec:
            add_issue(
                "sanction_date",
                "DATA_QUALITY_ISSUE",
                ValidationRuleCode.DQ_INVALID_DATE_ORDER,
                "ERROR",
                f"Sanction date ({d_sanc.strftime('%Y-%m-%d')}) precedes recommendation date ({d_rec.strftime('%Y-%m-%d')}).",
                d_sanc.strftime("%Y-%m-%d"),
                f"sanction_date >= recommendation_date ({d_rec.strftime('%Y-%m-%d')})",
            )

        if d_sanc and d_comp and d_comp < d_sanc:
            add_issue(
                "actual_completion_date",
                "DATA_QUALITY_ISSUE",
                ValidationRuleCode.DQ_INVALID_DATE_ORDER,
                "ERROR",
                f"Actual completion date ({d_comp.strftime('%Y-%m-%d')}) precedes sanction date ({d_sanc.strftime('%Y-%m-%d')}).",
                d_comp.strftime("%Y-%m-%d"),
                f"actual_completion_date >= sanction_date ({d_sanc.strftime('%Y-%m-%d')})",
            )

        if d_comm and d_comp and d_comp < d_comm:
            add_issue(
                "actual_completion_date",
                "DATA_QUALITY_ISSUE",
                ValidationRuleCode.DQ_INVALID_DATE_ORDER,
                "ERROR",
                f"Actual completion date ({d_comp.strftime('%Y-%m-%d')}) precedes commencement date ({d_comm.strftime('%Y-%m-%d')}).",
                d_comp.strftime("%Y-%m-%d"),
                f"actual_completion_date >= commencement_date ({d_comm.strftime('%Y-%m-%d')})",
            )

        # 8. Missing Completion Evidence
        if status == STATUS_COMPLETED or progress_pct >= 100.0:
            if not d_comp:
                add_issue(
                    "actual_completion_date",
                    "COMPLIANCE_RULE_VIOLATION",
                    ValidationRuleCode.RULE_MISSING_COMPLETION_EVIDENCE,
                    "WARNING",
                    "Work is recorded with status 'Completed' / 100% progress but lacks actual completion certificate date.",
                    "None/Empty",
                    "Valid actual_completion_date for completed works",
                )

        # 9. Geo-coordinates validation
        raw_lat = record.get("latitude")
        raw_lon = record.get("longitude")
        if raw_lat is None or raw_lon is None or str(raw_lat).strip() == "" or str(raw_lon).strip() == "":
            add_issue(
                "coordinates",
                "DATA_QUALITY_ISSUE",
                ValidationRuleCode.DQ_COORDINATES_OUT_OF_BOUNDS,
                "WARNING",
                "Geographic coordinates (latitude/longitude) are missing.",
                f"lat={raw_lat}, lon={raw_lon}",
                "Valid GPS latitude and longitude values",
            )
        else:
            try:
                lat_f = float(raw_lat)
                lon_f = float(raw_lon)
                if not (INDIA_GEO_BOUNDS["min_lat"] <= lat_f <= INDIA_GEO_BOUNDS["max_lat"] and
                        INDIA_GEO_BOUNDS["min_lon"] <= lon_f <= INDIA_GEO_BOUNDS["max_lon"]):
                    add_issue(
                        "coordinates",
                        "DATA_QUALITY_ISSUE",
                        ValidationRuleCode.DQ_COORDINATES_OUT_OF_BOUNDS,
                        "WARNING",
                        f"Coordinates ({lat_f}, {lon_f}) are outside valid India bounding box (Lat {INDIA_GEO_BOUNDS['min_lat']}-{INDIA_GEO_BOUNDS['max_lat']}, Lon {INDIA_GEO_BOUNDS['min_lon']}-{INDIA_GEO_BOUNDS['max_lon']}).",
                        f"({lat_f}, {lon_f})",
                        f"Lat: {INDIA_GEO_BOUNDS['min_lat']}-{INDIA_GEO_BOUNDS['max_lat']}, Lon: {INDIA_GEO_BOUNDS['min_lon']}-{INDIA_GEO_BOUNDS['max_lon']}",
                    )
            except (ValueError, TypeError):
                add_issue(
                    "coordinates",
                    "DATA_QUALITY_ISSUE",
                    ValidationRuleCode.DQ_COORDINATES_OUT_OF_BOUNDS,
                    "WARNING",
                    f"Non-numeric coordinates provided: lat='{raw_lat}', lon='{raw_lon}'.",
                    f"({raw_lat}, {raw_lon})",
                    "Floating point coordinate pair",
                )

        return issues

    def validate_dataset(self, records: List[Dict[str, Any]]) -> Tuple[ValidationSummary, List[ValidationIssue]]:
        """
        Validates an entire batch/list of work records and returns summary metrics along with issue details.
        """
        seen_work_ids: Set[str] = set()
        all_issues: List[ValidationIssue] = []
        invalid_row_set: Set[int] = set()

        for idx, rec in enumerate(records):
            row_num = idx + 1
            row_issues = self.validate_work_record(rec, row_num, seen_work_ids)
            if row_issues:
                # If there are ERROR or CRITICAL severity issues, mark row as invalid
                has_error = any(iss.severity in ["CRITICAL", "ERROR"] for iss in row_issues)
                if has_error:
                    invalid_row_set.add(row_num)
                all_issues.extend(row_issues)

        total = len(records)
        invalid = len(invalid_row_set)
        valid = total - invalid

        sev_counts: Dict[str, int] = {"CRITICAL": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}
        rule_counts: Dict[str, int] = {}
        cat_counts: Dict[str, int] = {"DATA_QUALITY_ISSUE": 0, "COMPLIANCE_RULE_VIOLATION": 0, "SUSPICIOUS_ANOMALY": 0}

        for iss in all_issues:
            sev_counts[iss.severity] = sev_counts.get(iss.severity, 0) + 1
            rule_counts[iss.rule_code] = rule_counts.get(iss.rule_code, 0) + 1
            cat_counts[iss.issue_category] = cat_counts.get(iss.issue_category, 0) + 1

        quality_score = round((valid / max(1, total)) * 100.0, 2)

        summary = ValidationSummary(
            total_records=total,
            valid_records=valid,
            invalid_records=invalid,
            total_issues=len(all_issues),
            issues_by_severity=sev_counts,
            issues_by_rule=rule_counts,
            issues_by_category=cat_counts,
            data_quality_score_pct=quality_score,
            validation_timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            synthetic_demo_data=True,
        )

        return summary, all_issues
