"""
CSV Upload Ingestion Mapper and Schema Normalizer for MPLADS data.
Allows flexible header aliases, type coercion, and schema sanitization for backend upload pipelines.
"""

from typing import Dict, List, Any, Optional, Tuple
import csv
import io
import re


class CSVMappingConfig:
    """
    Standard column alias mapping dictionary.
    Maps various real-world or legacy CSV headers to standard internal field keys.
    """
    DEFAULT_ALIASES: Dict[str, List[str]] = {
        "work_id": ["work_id", "work id", "work_code", "project_id", "workid", "id", "work_number"],
        "state": ["state", "state_name", "state / ut", "state_ut"],
        "district": ["district", "district_name", "dist_name", "district / zilla"],
        "constituency": ["constituency", "parliamentary_constituency", "pc_name", "constituency_name", "ls_constituency"],
        "mp_reference": ["mp_reference", "mp_name", "mp_code", "hon_mp_ref", "mp_id", "mp_ref"],
        "mp_house": ["mp_house", "house", "parliament_house", "mp_type"],
        "work_title": ["work_title", "work_name", "project_title", "title", "work_description", "description"],
        "category": ["category", "work_category", "sector", "head_of_development", "work_type"],
        "agency_id": ["agency_id", "implementing_agency_id", "agency_code"],
        "agency_name": ["agency_name", "implementing_agency", "executing_agency", "agency", "contractor_agency"],
        "status": ["status", "work_status", "current_status", "project_status", "stage"],
        "estimate_amount": ["estimate_amount", "estimated_cost", "estimate_cost", "estimate (rs)", "estimate_rs", "estimated_amount_inr"],
        "sanctioned_amount": ["sanctioned_amount", "sanction_amount", "sanction_cost", "sanctioned_cost", "sanction (rs)", "sanction_rs"],
        "cumulative_payments": ["cumulative_payments", "total_payments", "payments_released", "disbursed_amount", "released_amount", "payments (rs)"],
        "expenditure": ["expenditure", "total_expenditure", "expenditure_incurred", "expenditure (rs)", "actual_expenditure"],
        "physical_progress_pct": ["physical_progress_pct", "physical_progress", "progress_percentage", "progress_%", "progress_pct", "progress"],
        "recommendation_date": ["recommendation_date", "date_of_recommendation", "recommended_on", "rec_date"],
        "sanction_date": ["sanction_date", "date_of_sanction", "sanctioned_on", "as_date"],
        "work_order_date": ["work_order_date", "date_of_work_order", "wo_date", "tender_allotment_date"],
        "commencement_date": ["commencement_date", "start_date", "date_of_commencement", "work_commenced_on"],
        "target_completion_date": ["target_completion_date", "scheduled_completion_date", "target_date", "stipulated_date"],
        "actual_completion_date": ["actual_completion_date", "completion_date", "date_of_completion", "completed_on"],
        "latitude": ["latitude", "lat", "geo_lat", "gps_latitude", "y_coord"],
        "longitude": ["longitude", "lon", "long", "geo_lon", "gps_longitude", "x_coord"],
        "synthetic_demo_data": ["synthetic_demo_data", "is_synthetic", "demo_data_flag"],
    }


class IngestionMapper:
    """
    Maps and transforms arbitrary CSV inputs into standardized dictionaries matching MPLADS schemas.
    """

    def __init__(self, custom_aliases: Optional[Dict[str, List[str]]] = None):
        self.aliases = custom_aliases or CSVMappingConfig.DEFAULT_ALIASES
        # Build inverted lookup table for O(1) matching: normalized_header -> canonical_field
        self._lookup: Dict[str, str] = {}
        for canonical, alias_list in self.aliases.items():
            self._lookup[self._normalize(canonical)] = canonical
            for a in alias_list:
                self._lookup[self._normalize(a)] = canonical

    @staticmethod
    def _normalize(header: str) -> str:
        return re.sub(r"[^a-z0-9]", "", str(header).lower().strip())

    @staticmethod
    def _clean_numeric(val: Any) -> Optional[float]:
        if val is None or str(val).strip() == "" or str(val).lower() in ["none", "null", "nan", "-"]:
            return 0.0
        val_str = str(val).strip().lower()
        
        # Parse Indian currency units (Crores, Lakhs, Thousands)
        multiplier = 1.0
        if re.search(r"(?:\bcrores?\b|\bcr\b)", val_str):
            multiplier = 10_000_000.0
            val_str = re.sub(r"(?:\bcrores?\b|\bcr\b)", "", val_str)
        elif re.search(r"(?:\blakhs?\b|\blacs?\b)", val_str):
            multiplier = 100_000.0
            val_str = re.sub(r"(?:\blakhs?\b|\blacs?\b)", "", val_str)
        elif re.search(r"(?:\bthousands?\b|\bk\b)", val_str):
            multiplier = 1_000.0
            val_str = re.sub(r"(?:\bthousands?\b|\bk\b)", "", val_str)

        # Remove currency indicators (INR, Rs, Rs.), symbols (₹), commas, percent signs, and whitespace
        cleaned = re.sub(r"(?:inr|rs\.?|[₹,%]|\s)", "", val_str)
        try:
            return float(cleaned) * multiplier
        except ValueError:
            return None





    @staticmethod
    def _clean_string(val: Any) -> str:
        if val is None or str(val).lower() in ["none", "null", "nan"]:
            return ""
        return str(val).strip()

    def map_row(self, raw_row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps a single CSV row dictionary to normalized field names and sanitized types.
        """
        mapped: Dict[str, Any] = {}
        for header, value in raw_row.items():
            norm = self._normalize(header)
            canonical = self._lookup.get(norm)
            if canonical:
                mapped[canonical] = value

        # Standardize numeric fields
        for num_field in ["estimate_amount", "sanctioned_amount", "cumulative_payments", "expenditure", "physical_progress_pct"]:
            if num_field in mapped:
                mapped[num_field] = self._clean_numeric(mapped[num_field])

        # Standardize coordinates
        for coord in ["latitude", "longitude"]:
            if coord in mapped:
                val = self._clean_numeric(mapped[coord])
                mapped[coord] = val if val != 0.0 else None

        # Standardize string fields
        for str_field in ["work_id", "state", "district", "constituency", "mp_reference", "work_title", "category", "agency_id", "agency_name", "status"]:
            if str_field in mapped:
                mapped[str_field] = self._clean_string(mapped[str_field])

        # Ensure synthetic_demo_data flag is True
        mapped["synthetic_demo_data"] = True

        return mapped

    def parse_csv_content(self, csv_content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parses CSV string content into a list of normalized row dictionaries and detected column headers.
        """
        reader = csv.DictReader(io.StringIO(csv_content))
        detected_headers = reader.fieldnames or []
        records = []
        for raw_row in reader:
            records.append(self.map_row(raw_row))
        return records, list(detected_headers)

    def parse_csv_file(self, file_path: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parses a local CSV file into normalized records.
        """
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            detected_headers = reader.fieldnames or []
            records = []
            for raw_row in reader:
                records.append(self.map_row(raw_row))
        return records, list(detected_headers)
