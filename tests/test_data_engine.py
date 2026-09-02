"""
Comprehensive Unit & Integration Test Suite for MPLADS Synthetic Data Engine & Ingestion Pipeline.
Compatible with standard library unittest as well as pytest.
"""

import unittest
import os
import sys
from pathlib import Path

# Ensure repo root is on sys.path
repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from data.synthetic_generator.constants import (
    CATEGORIES,
    STATE_DISTRICT_MASTER,
    STATUS_COMPLETED,
    STATUS_IN_PROGRESS,
    STATUS_STALLED,
    STATUS_RECOMMENDED,
)
from data.synthetic_generator.schemas import (
    WorkRecord,
    PaymentRecord,
    ProgressUpdateRecord,
    AgencyRecord,
    InspectionRecord,
    UnifiedWorkDemoRecord,
)
from data.synthetic_generator.generator import MPLADSDataGenerator
from data.synthetic_generator.validator import MPLADSDataValidator, ValidationRuleCode
from data.synthetic_generator.ingestion_mapper import IngestionMapper, CSVMappingConfig
from data.synthetic_generator.report_formatter import ValidationReportFormatter
from data.synthetic_generator.anomalies import AnomalyType
from backend.app.services.data_ingestion import DataIngestionService
from backend.app.services.validation import ValidationService


class TestSyntheticDataGenerator(unittest.TestCase):
    """Tests for the generator engine, scale criteria, and reproducibility."""

    def test_seed_reproducibility(self):
        """Verify that identical seeds produce identical datasets."""
        gen1 = MPLADSDataGenerator(seed=123)
        data1 = gen1.generate_all(num_works=50, is_dirty=False)
        
        gen2 = MPLADSDataGenerator(seed=123)
        data2 = gen2.generate_all(num_works=50, is_dirty=False)

        self.assertEqual(len(data1["works"]), len(data2["works"]))
        self.assertEqual(data1["works"][0]["work_id"], data2["works"][0]["work_id"])
        self.assertEqual(data1["works"][0]["work_title"], data2["works"][0]["work_title"])
        self.assertEqual(data1["works"][0]["sanctioned_amount"], data2["works"][0]["sanctioned_amount"])
        self.assertEqual(len(data1["payments"]), len(data2["payments"]))

    def test_scale_targets(self):
        """Verify that generator satisfies all minimum volume thresholds on standard run."""
        gen = MPLADSDataGenerator(seed=42)
        data = gen.generate_all(num_works=10000, is_dirty=False)
        unified = gen.build_unified_records()

        self.assertGreaterEqual(len(data["works"]), 10000, f"Expected >= 10,000 works, got {len(data['works'])}")
        self.assertGreaterEqual(len(data["payments"]), 30000, f"Expected >= 30,000 payments, got {len(data['payments'])}")
        self.assertGreaterEqual(len(data["progress_updates"]), 40000, f"Expected >= 40,000 progress updates, got {len(data['progress_updates'])}")
        self.assertGreaterEqual(len(data["agencies"]), 250, f"Expected >= 250 agencies, got {len(data['agencies'])}")
        self.assertGreaterEqual(len(data["inspections"]), 10000, f"Expected >= 10,000 inspections, got {len(data['inspections'])}")
        self.assertGreaterEqual(len(data["sanctions"]), 9000, f"Expected >= 9,000 sanctions, got {len(data['sanctions'])}")
        self.assertGreaterEqual(len(data["estimates"]), 10000, f"Expected >= 10,000 estimates, got {len(data['estimates'])}")
        self.assertGreaterEqual(len(data["assets"]), 4000, f"Expected >= 4,000 assets, got {len(data['assets'])}")
        self.assertEqual(len(unified), len(data["works"]))

    def test_synthetic_flag_mandatory(self):
        """Verify that all records across all entities carry synthetic_demo_data=True."""
        gen = MPLADSDataGenerator(seed=99)
        data = gen.generate_all(num_works=100, is_dirty=True)
        unified = gen.build_unified_records()

        for entity_name, records in data.items():
            for r in records:
                self.assertTrue(r.get("synthetic_demo_data") is True, f"Missing synthetic flag on {entity_name} record {r}")

        for u in unified:
            self.assertTrue(u.get("synthetic_demo_data") is True)

    def test_category_consistency(self):
        """Verify that all generated works use only standard peer-group categories."""
        gen = MPLADSDataGenerator(seed=42)
        data = gen.generate_all(num_works=200, is_dirty=False)
        for w in data["works"]:
            self.assertIn(w["category"], CATEGORIES)


class TestValidationEngine(unittest.TestCase):
    """Tests for each validation rule and data quality constraint."""

    def setUp(self):
        self.validator = MPLADSDataValidator()

    def test_clean_dataset_zero_critical_errors(self):
        """Verify that clean generated dataset passes with zero CRITICAL or ERROR issues."""
        gen = MPLADSDataGenerator(seed=42)
        gen.generate_all(num_works=500, is_dirty=False)
        unified = gen.build_unified_records()

        summary, issues = self.validator.validate_dataset(unified)
        self.assertEqual(summary.issues_by_severity["CRITICAL"], 0)
        self.assertEqual(summary.issues_by_severity["ERROR"], 0)
        self.assertEqual(summary.data_quality_score_pct, 100.0)

    def test_rule_missing_primary_key(self):
        rec = {
            "work_id": "",
            "category": "Drinking Water",
            "state": "Maharashtra",
            "district": "Pune",
        }
        issues = self.validator.validate_work_record(rec, 1, set())
        codes = [i.rule_code for i in issues]
        self.assertIn(ValidationRuleCode.DQ_MISSING_PRIMARY_KEY, codes)

    def test_rule_duplicate_work_id(self):
        seen = {"MPLAD-WRK-000001"}
        rec = {
            "work_id": "MPLAD-WRK-000001",
            "category": "Drinking Water",
            "state": "Maharashtra",
            "district": "Pune",
        }
        issues = self.validator.validate_work_record(rec, 2, seen)
        codes = [i.rule_code for i in issues]
        self.assertIn(ValidationRuleCode.DQ_DUPLICATE_WORK_ID, codes)

    def test_rule_negative_amount(self):
        rec = {
            "work_id": "MPLAD-WRK-000002",
            "category": "Drinking Water",
            "state": "Maharashtra",
            "district": "Pune",
            "sanctioned_amount": -150000.0,
        }
        issues = self.validator.validate_work_record(rec, 1, set())
        codes = [i.rule_code for i in issues]
        self.assertIn(ValidationRuleCode.DQ_NEGATIVE_AMOUNT, codes)

    def test_rule_payments_exceed_sanction(self):
        rec = {
            "work_id": "MPLAD-WRK-000003",
            "category": "Education Infrastructure",
            "state": "Maharashtra",
            "district": "Pune",
            "sanctioned_amount": 1000000.0,
            "cumulative_payments": 1500000.0,
        }
        issues = self.validator.validate_work_record(rec, 1, set())
        codes = [i.rule_code for i in issues]
        self.assertIn(ValidationRuleCode.RULE_PAYMENTS_EXCEED_SANCTION, codes)

    def test_rule_progress_out_of_range(self):
        rec = {
            "work_id": "MPLAD-WRK-000004",
            "category": "Health & Sanitation",
            "state": "Maharashtra",
            "district": "Pune",
            "physical_progress_pct": 145.0,
        }
        issues = self.validator.validate_work_record(rec, 1, set())
        codes = [i.rule_code for i in issues]
        self.assertIn(ValidationRuleCode.DQ_PROGRESS_OUT_OF_RANGE, codes)

    def test_rule_invalid_date_order(self):
        rec = {
            "work_id": "MPLAD-WRK-000005",
            "category": "Drinking Water",
            "state": "Maharashtra",
            "district": "Pune",
            "recommendation_date": "2024-05-01",
            "sanction_date": "2024-02-01",  # Sanction before recommendation
        }
        issues = self.validator.validate_work_record(rec, 1, set())
        codes = [i.rule_code for i in issues]
        self.assertIn(ValidationRuleCode.DQ_INVALID_DATE_ORDER, codes)

    def test_rule_missing_completion_evidence(self):
        rec = {
            "work_id": "MPLAD-WRK-000006",
            "category": "Drinking Water",
            "state": "Maharashtra",
            "district": "Pune",
            "status": STATUS_COMPLETED,
            "physical_progress_pct": 100.0,
            "actual_completion_date": None,  # Missing completion date
        }
        issues = self.validator.validate_work_record(rec, 1, set())
        codes = [i.rule_code for i in issues]
        self.assertIn(ValidationRuleCode.RULE_MISSING_COMPLETION_EVIDENCE, codes)

    def test_rule_invalid_state_district(self):
        rec = {
            "work_id": "MPLAD-WRK-000007",
            "category": "Drinking Water",
            "state": "Tamil Nadu",
            "district": "Nagpur",  # Nagpur is in Maharashtra
        }
        issues = self.validator.validate_work_record(rec, 1, set())
        codes = [i.rule_code for i in issues]
        self.assertIn(ValidationRuleCode.DQ_INVALID_STATE_DISTRICT, codes)

    def test_rule_coordinates_out_of_bounds(self):
        rec = {
            "work_id": "MPLAD-WRK-000008",
            "category": "Drinking Water",
            "state": "Maharashtra",
            "district": "Pune",
            "latitude": 85.50,  # Latitude 85.5 is out of India bounds (6.0 - 38.0)
            "longitude": 73.85,
        }
        issues = self.validator.validate_work_record(rec, 1, set())
        codes = [i.rule_code for i in issues]
        self.assertIn(ValidationRuleCode.DQ_COORDINATES_OUT_OF_BOUNDS, codes)


class TestAnomalyInjection(unittest.TestCase):
    """Tests for injected demonstration scenarios in the dirty dataset."""

    def test_injected_scenarios_presence_and_labels(self):
        gen = MPLADSDataGenerator(seed=42)
        dirty_data = gen.generate_all(num_works=1000, is_dirty=True, anomaly_rate=0.15)
        works = dirty_data["works"]

        anomaly_types = {w.get("anomaly_type") for w in works if w.get("is_anomaly")}
        
        self.assertIn(AnomalyType.PAYMENT_PROGRESS_MISMATCH, anomaly_types)
        self.assertIn(AnomalyType.COST_OUTLIER, anomaly_types)
        self.assertIn(AnomalyType.STALLED_WORK, anomaly_types)
        self.assertIn(AnomalyType.POSSIBLE_DUPLICATE, anomaly_types)
        self.assertIn(AnomalyType.MISSING_COMPLETION_EVIDENCE, anomaly_types)
        self.assertIn(AnomalyType.DATA_QUALITY_ISSUE, anomaly_types)

        # Verify duplicate pointers
        duplicates = [w for w in works if w.get("anomaly_type") == AnomalyType.POSSIBLE_DUPLICATE]
        self.assertGreater(len(duplicates), 0)
        for d in duplicates:
            self.assertIsNotNone(d.get("duplicate_of_work_id"))


class TestIngestionMapperAndBackendServices(unittest.TestCase):
    """Tests for CSV column mapping, aliasing, and backend services."""

    def test_ingestion_mapper_aliases_and_cleaning(self):
        mapper = IngestionMapper()
        raw_row = {
            "Work ID": "MPLAD-WRK-999999",
            "State / UT": "Maharashtra",
            "District Name": "Pune",
            "PC_Name": "Pune Parliamentary Constituency",
            "Hon_MP_Ref": "MP-LOK-DEMO-001",
            "Project Title": "Construction of Solar Light Unit",
            "Work Category": "Renewable & Solar Energy",
            "Implementing Agency": "Pune Municipal Engineering Cell Unit-1",
            "Work Status": "In Progress",
            "Estimate (Rs)": "₹ 15,00,000",
            "Sanction Cost": "1500000.00",
            "Payments Released": "₹ 7,50,000.00",
            "Expenditure (Rs)": "680000",
            "Progress %": "50.0%",
            "Recommendation Date": "2024-01-10",
            "Sanction Date": "2024-02-15",
            "Lat": "18.5204",
            "Long": "73.8567",
        }

        mapped = mapper.map_row(raw_row)
        self.assertEqual(mapped["work_id"], "MPLAD-WRK-999999")
        self.assertEqual(mapped["state"], "Maharashtra")
        self.assertEqual(mapped["district"], "Pune")
        self.assertEqual(mapped["category"], "Renewable & Solar Energy")
        self.assertEqual(mapped["estimate_amount"], 1500000.0)
        self.assertEqual(mapped["cumulative_payments"], 750000.0)
        self.assertEqual(mapped["physical_progress_pct"], 50.0)
        self.assertEqual(mapped["latitude"], 18.5204)
        self.assertEqual(mapped["longitude"], 73.8567)
        self.assertTrue(mapped["synthetic_demo_data"])

    def test_data_ingestion_service(self):
        service = DataIngestionService()
        csv_content = """Work ID,State,District,Constituency,MP_Reference,Work Title,Category,Agency,Status,Estimate (Rs),Sanction (Rs),Payments (Rs),Expenditure (Rs),Progress %,Recommendation Date,Sanction Date,Lat,Lon
MPLAD-TEST-001,Maharashtra,Pune,Pune Parliamentary Constituency,MP-LOK-DEMO-001,Installation of Solar High-Mast Lights,Renewable & Solar Energy,Pune Solar Unit,In Progress,800000,800000,400000,380000,50.0,2024-01-10,2024-02-10,18.5204,73.8567
MPLAD-TEST-002,Maharashtra,Pune,Pune Parliamentary Constituency,MP-LOK-DEMO-001,Construction of RO Plant,Drinking Water,Pune Water Unit,In Progress,500000,-500000,100000,90000,20.0,2024-01-10,2024-02-10,18.5204,73.8567
"""
        result = service.process_csv_upload(csv_content, filename="test_upload.csv")
        self.assertEqual(result["total_records"], 2)
        self.assertEqual(result["status"], "FAILED_VALIDATION")  # Second record has negative sanction amount
        report = result["validation_report"]
        self.assertEqual(report["summary"]["invalid_records"], 1)
        self.assertEqual(report["summary"]["valid_records"], 1)

    def test_validation_service_single_record(self):
        val_service = ValidationService()
        rec = {
            "work_id": "MPLAD-WRK-000010",
            "category": "Invalid Category XYZ",
            "state": "Maharashtra",
            "district": "Pune",
        }
        issues = val_service.validate_single_record(rec)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any(i["rule_code"] == ValidationRuleCode.DQ_INVALID_CATEGORY for i in issues))


if __name__ == "__main__":
    unittest.main()
