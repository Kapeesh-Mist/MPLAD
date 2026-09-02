#!/usr/bin/env python3
"""
CLI Runner for MPLADS Synthetic Demonstration Data Engine.
Generates reproducible synthetic datasets, validates compliance, exports CSV and JSON reports.

Usage:
    python data/synthetic_generator/generate_mplads_data.py --seed 42 --num-works 10000 --output-dir data/sample --export-relational --validate
"""

import os
import sys
import argparse
import csv
import json
from pathlib import Path
from typing import List, Dict, Any

# Ensure local package imports work regardless of CWD
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generator import MPLADSDataGenerator
from validator import MPLADSDataValidator
from report_formatter import ValidationReportFormatter



def export_csv(records: List[Dict[str, Any]], file_path: str) -> None:
    """Exports a list of dictionaries to a CSV file."""
    if not records:
        return
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main():
    parser = argparse.ArgumentParser(
        description="MPLADS Synthetic Demonstration Data Generator & Validation CLI"
    )
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed (default: 42)")
    parser.add_argument("--num-works", type=int, default=10000, help="Number of works to generate (default: 10000)")
    parser.add_argument("--anomaly-rate", type=float, default=0.08, help="Anomaly injection rate for dirty dataset (default: 0.08)")
    parser.add_argument("--output-dir", type=str, default="data/sample", help="Output directory for generated datasets")
    parser.add_argument("--export-relational", action="store_true", default=True, help="Export normalized relational CSV tables")
    parser.add_argument("--validate", action="store_true", default=True, help="Execute validation and generate JSON reports")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("MPLADS SYNTHETIC DATA ENGINE")
    print(f"Seed: {args.seed} | Target Works: {args.num_works} | Output: {args.output_dir}")
    print("=" * 70)

    # 1. Generate Clean Dataset
    print("\n[1/4] Generating Clean Dataset...")
    clean_gen = MPLADSDataGenerator(seed=args.seed)
    clean_data = clean_gen.generate_all(num_works=args.num_works, is_dirty=False)
    clean_unified = clean_gen.build_unified_records()

    print(f"  -> Generated {len(clean_data['works']):,} Works")
    print(f"  -> Generated {len(clean_data['payments']):,} Payments")
    print(f"  -> Generated {len(clean_data['progress_updates']):,} Progress Updates")
    print(f"  -> Generated {len(clean_data['agencies']):,} Implementing Agencies")
    print(f"  -> Generated {len(clean_data['inspections']):,} Inspection Records")
    print(f"  -> Generated {len(clean_data['sanctions']):,} Administrative Sanctions")
    print(f"  -> Generated {len(clean_data['estimates']):,} Technical Estimates")
    print(f"  -> Generated {len(clean_data['assets']):,} Physical Assets")

    clean_csv_path = output_dir / "clean_mplads_demo.csv"
    print(f"  -> Saving unified clean CSV: {clean_csv_path}")
    export_csv(clean_unified, str(clean_csv_path))

    if args.export_relational:
        rel_clean_dir = output_dir / "relational" / "clean"
        for entity_name, records in clean_data.items():
            rel_file = rel_clean_dir / f"{entity_name}.csv"
            export_csv(records, str(rel_file))
        print(f"  -> Saved normalized relational clean tables in {rel_clean_dir}")

    # 2. Generate Dirty Dataset with Injected Demonstration Scenarios
    print("\n[2/4] Generating Dirty Dataset with Injected Scenarios...")
    dirty_gen = MPLADSDataGenerator(seed=args.seed)
    dirty_data = dirty_gen.generate_all(
        num_works=args.num_works,
        is_dirty=True,
        anomaly_rate=args.anomaly_rate
    )
    dirty_unified = dirty_gen.build_unified_records()

    dirty_csv_path = output_dir / "dirty_mplads_demo.csv"
    print(f"  -> Saving unified dirty CSV: {dirty_csv_path}")
    export_csv(dirty_unified, str(dirty_csv_path))

    if args.export_relational:
        rel_dirty_dir = output_dir / "relational" / "dirty"
        for entity_name, records in dirty_data.items():
            rel_file = rel_dirty_dir / f"{entity_name}.csv"
            export_csv(records, str(rel_file))
        print(f"  -> Saved normalized relational dirty tables in {rel_dirty_dir}")

    # 3. Validation & Report Generation
    if args.validate:
        print("\n[3/4] Validating Clean Dataset...")
        validator = MPLADSDataValidator()
        clean_summary, clean_issues = validator.validate_dataset(clean_unified)
        clean_report = ValidationReportFormatter.build_report(
            summary=clean_summary,
            issues=clean_issues,
            source_filename="clean_mplads_demo.csv",
        )
        clean_report_path = output_dir / "clean_validation_report.json"
        ValidationReportFormatter.export_json(clean_report, str(clean_report_path))
        print(f"  -> Clean Dataset Quality Score: {clean_summary.data_quality_score_pct}%")
        print(f"  -> Total Issues in Clean Dataset: {clean_summary.total_issues}")
        print(f"  -> Clean Validation Report saved: {clean_report_path}")

        print("\n[4/4] Validating Dirty Dataset...")
        dirty_summary, dirty_issues = validator.validate_dataset(dirty_unified)
        dirty_report = ValidationReportFormatter.build_report(
            summary=dirty_summary,
            issues=dirty_issues,
            source_filename="dirty_mplads_demo.csv",
        )
        dirty_report_path = output_dir / "dirty_validation_report.json"
        ValidationReportFormatter.export_json(dirty_report, str(dirty_report_path))
        print(f"  -> Dirty Dataset Quality Score: {dirty_summary.data_quality_score_pct}%")
        print(f"  -> Total Detected Issues in Dirty Dataset: {dirty_summary.total_issues}")
        print(f"  -> Issues by Severity: {dirty_summary.issues_by_severity}")
        print(f"  -> Dirty Validation Report saved: {dirty_report_path}")

    print("\n" + "=" * 70)
    print("EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
