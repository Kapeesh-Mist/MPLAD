from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional


VALID_WORK_STATUSES = {
    "Recommended",
    "Sanctioned",
    "Under Implementation",
    "Completed",
    "Cancelled",
}


@dataclass
class CanonicalWorkRecord:
    work_id: str
    state: str
    district: str
    constituency: str
    work_title: str
    work_category: str
    implementing_agency_id: str

    sanction_date: Optional[date]
    estimated_cost: float
    sanctioned_cost: float
    amount_paid: float
    expenditure_reported: float
    physical_progress_percent: float

    expected_completion_date: Optional[date]
    last_progress_update: Optional[date]
    status: str

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    completion_date: Optional[date] = None
    estimate_revision_count: int = 0

    asset_type: Optional[str] = None
    document_ids: List[str] = field(default_factory=list)
    inspection_ids: List[str] = field(default_factory=list)

    hierarchy_path: Optional[str] = None
    source_system: str = "demo_csv"
    metadata: Dict[str, Any] = field(default_factory=dict)