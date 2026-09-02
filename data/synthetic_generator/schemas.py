"""
Data schemas and models for MPLADS Synthetic Data Engine.
Provides both normalized relational entity models and flattened unified demonstration models.
All schemas include synthetic_demo_data=True.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import json


@dataclass
class AgencyRecord:
    agency_id: str
    agency_name: str
    agency_type: str  # e.g., "Public Works Dept (Demo)", "Rural Development Agency (Demo)", "Municipal Corporation (Demo)", "Irrigation Board (Demo)"
    state: str
    district: str
    nodal_officer_designation: str
    contact_email_synthetic: str
    performance_rating: float  # 1.0 to 5.0
    active_status: str  # "Active", "Suspended (Demo)", "Inactive"
    synthetic_demo_data: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EstimateRecord:
    estimate_id: str
    work_id: str
    prepared_date: str
    technical_sanction_date: Optional[str]
    estimated_amount: float
    contingency_pct: float
    schedule_of_rates_year: int
    technical_authority: str
    synthetic_demo_data: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SanctionRecord:
    sanction_id: str
    work_id: str
    sanction_order_number: str
    sanction_date: str
    sanctioned_amount: float
    installment_schedule: str  # e.g., "50-40-10", "40-40-20", "100"
    approving_authority: str
    synthetic_demo_data: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PaymentRecord:
    payment_id: str
    work_id: str
    installment_number: int
    payment_date: str
    amount: float
    voucher_number: str
    payee_agency_id: str
    disbursement_mode: str  # "PFMS_DEMO_TRANSFER", "DIRECT_BENEFIT_DEMO", "TREASURY_TRANSFER_DEMO"
    payment_status: str  # "Disbursed", "Pending Clearance", "Rejected"
    synthetic_demo_data: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProgressUpdateRecord:
    update_id: str
    work_id: str
    update_date: str
    physical_progress_pct: float
    stage_name: str  # "Planning", "Foundation", "Structural Work", "Finishing", "Commissioning", "Completed"
    expenditure_to_date: float
    reported_by_designation: str
    remarks: str
    geo_tagged_photo_ref: Optional[str]
    synthetic_demo_data: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InspectionRecord:
    inspection_id: str
    work_id: str
    inspection_date: str
    inspector_designation: str
    inspection_stage: str
    rating: str  # "Satisfactory", "Good", "Excellent", "Requires Rectification", "Non-Compliant"
    findings_summary: str
    defects_observed: bool
    rectification_deadline: Optional[str]
    inspection_photo_ref: Optional[str]
    synthetic_demo_data: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AssetRecord:
    asset_id: str
    work_id: str
    asset_name: str
    category: str
    location_description: str
    latitude: float
    longitude: float
    handover_date: Optional[str]
    custodian_department: str
    maintenance_status: str  # "Operational", "Under Maintenance", "Requires Repair", "Decommissioned"
    synthetic_demo_data: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkRecord:
    work_id: str
    state: str
    district: str
    constituency: str
    mp_reference: str
    mp_house: str  # "Lok Sabha (Demo)", "Rajya Sabha (Demo)"
    work_title: str
    category: str
    agency_id: str
    agency_name: str
    status: str
    
    # Financials
    estimate_amount: float
    sanctioned_amount: float
    cumulative_payments: float
    expenditure: float
    
    # Progress
    physical_progress_pct: float
    
    # Dates
    recommendation_date: str
    sanction_date: Optional[str]
    work_order_date: Optional[str]
    commencement_date: Optional[str]
    target_completion_date: Optional[str]
    actual_completion_date: Optional[str]
    
    # Geolocation
    latitude: Optional[float]
    longitude: Optional[float]
    
    # Demonstration / Anomaly Ground Truth (for AI evaluation & benchmarks)
    is_anomaly: bool = False
    anomaly_type: Optional[str] = None  # None or "PAYMENT_PROGRESS_MISMATCH", "COST_OUTLIER", "STALLED_WORK", "POSSIBLE_DUPLICATE", "MISSING_COMPLETION_EVIDENCE", "DATA_QUALITY_ISSUE"
    anomaly_description: Optional[str] = None
    duplicate_of_work_id: Optional[str] = None
    
    # Compliance & Safety Flag
    synthetic_demo_data: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UnifiedWorkDemoRecord:
    """
    Flattened master table representation ideal for single-CSV demo exports,
    backend preview uploads, analytics dashboards, and ML training datasets.
    """
    work_id: str
    state: str
    district: str
    constituency: str
    mp_reference: str
    mp_house: str
    work_title: str
    category: str
    agency_id: str
    agency_name: str
    status: str
    estimate_amount: float
    sanctioned_amount: float
    cumulative_payments: float
    expenditure: float
    physical_progress_pct: float
    recommendation_date: str
    sanction_date: Optional[str]
    work_order_date: Optional[str]
    commencement_date: Optional[str]
    target_completion_date: Optional[str]
    actual_completion_date: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    latest_inspection_date: Optional[str]
    latest_inspection_rating: Optional[str]
    latest_inspector_designation: Optional[str]
    inspection_count: int
    payment_count: int
    progress_update_count: int
    is_anomaly: bool
    anomaly_type: Optional[str]
    anomaly_description: Optional[str]
    duplicate_of_work_id: Optional[str]
    synthetic_demo_data: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationIssue:
    issue_id: str
    row_number: int
    work_id: Optional[str]
    field_name: str
    issue_category: str  # "DATA_QUALITY_ISSUE" or "COMPLIANCE_RULE_VIOLATION" or "SUSPICIOUS_ANOMALY"
    rule_code: str
    severity: str  # "CRITICAL", "ERROR", "WARNING", "INFO"
    message: str
    invalid_value: Any
    expected_condition: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationSummary:
    total_records: int
    valid_records: int
    invalid_records: int
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_rule: Dict[str, int]
    issues_by_category: Dict[str, int]
    data_quality_score_pct: float
    validation_timestamp: str
    synthetic_demo_data: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
