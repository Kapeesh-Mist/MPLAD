"""
Backend Data Ingestion Service.
Handles CSV upload ingestion, column mapping, normalization, and connects to validation engine.
"""

from typing import Dict, List, Any, Optional, Tuple
import os
import sys

# Ensure data package is importable
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from data.synthetic_generator.ingestion_mapper import IngestionMapper, CSVMappingConfig
from data.synthetic_generator.validator import MPLADSDataValidator
from data.synthetic_generator.report_formatter import ValidationReportFormatter


class DataIngestionService:
    """
    Service layer orchestrating CSV uploads, schema mapping, and validation.
    """

    def __init__(self, custom_mapping: Optional[Dict[str, List[str]]] = None):
        self.mapper = IngestionMapper(custom_aliases=custom_mapping)
        self.validator = MPLADSDataValidator()

    def process_csv_upload(
        self,
        file_content: str,
        filename: str = "upload.csv",
        batch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parses uploaded CSV content, normalizes records, runs validation checks,
        and returns mapped records along with the full validation report.
        """
        records, detected_headers = self.mapper.parse_csv_content(file_content)
        summary, issues = self.validator.validate_dataset(records)
        report = ValidationReportFormatter.build_report(
            summary=summary,
            issues=issues,
            batch_id=batch_id,
            source_filename=filename,
        )

        return {
            "batch_id": report["metadata"]["batch_id"],
            "status": report["metadata"]["status"],
            "total_records": len(records),
            "detected_headers": detected_headers,
            "validation_report": report,
            "records": records,
        }

    def process_csv_file(
        self,
        file_path: str,
        batch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Loads and processes a CSV file from local disk path.
        """
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            content = f.read()
        return self.process_csv_upload(
            file_content=content,
            filename=os.path.basename(file_path),
            batch_id=batch_id,
        )
