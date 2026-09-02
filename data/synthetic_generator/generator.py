"""
Core Synthetic MPLADS Data Generator.
Produces deterministic, high-volume datasets meeting all target scale specifications:
- >= 10,000 works
- >= 30,000 payments
- >= 40,000 progress updates
- >= 250 agencies
- Sanctions, Estimates, Inspections, Assets
Supports clean generation and controlled anomaly/dirty data injection with seed reproducibility.
"""

import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional

try:
    from .constants import (
        SYNTHETIC_FLAG,
        CATEGORIES,
        CATEGORY_BENCHMARKS,
        STATE_DISTRICT_MASTER,
        TITLE_TEMPLATES,
        STATUS_RECOMMENDED,
        STATUS_SANCTIONED,
        STATUS_WORK_ORDER,
        STATUS_IN_PROGRESS,
        STATUS_COMPLETED,
        STATUS_CANCELLED,
        STATUS_STALLED,
        ALL_STATUSES,
        INSPECTOR_DESIGNATIONS,
        INSPECTION_RATINGS,
    )
    from .schemas import (
        AgencyRecord,
        EstimateRecord,
        SanctionRecord,
        PaymentRecord,
        ProgressUpdateRecord,
        InspectionRecord,
        AssetRecord,
        WorkRecord,
        UnifiedWorkDemoRecord,
    )
    from .anomalies import (
        AnomalyType,
        inject_payment_progress_mismatch,
        inject_cost_outlier,
        inject_stalled_work,
        create_duplicate_work_record,
        inject_missing_completion_evidence,
    )
except (ImportError, ValueError):
    from constants import (
        SYNTHETIC_FLAG,
        CATEGORIES,
        CATEGORY_BENCHMARKS,
        STATE_DISTRICT_MASTER,
        TITLE_TEMPLATES,
        STATUS_RECOMMENDED,
        STATUS_SANCTIONED,
        STATUS_WORK_ORDER,
        STATUS_IN_PROGRESS,
        STATUS_COMPLETED,
        STATUS_CANCELLED,
        STATUS_STALLED,
        ALL_STATUSES,
        INSPECTOR_DESIGNATIONS,
        INSPECTION_RATINGS,
    )
    from schemas import (
        AgencyRecord,
        EstimateRecord,
        SanctionRecord,
        PaymentRecord,
        ProgressUpdateRecord,
        InspectionRecord,
        AssetRecord,
        WorkRecord,
        UnifiedWorkDemoRecord,
    )
    from anomalies import (
        AnomalyType,
        inject_payment_progress_mismatch,
        inject_cost_outlier,
        inject_stalled_work,
        create_duplicate_work_record,
        inject_missing_completion_evidence,
    )



class MPLADSDataGenerator:
    """
    Deterministic Synthetic Data Generator for MPLADS demonstration datasets.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.agencies: List[Dict[str, Any]] = []
        self.works: List[Dict[str, Any]] = []
        self.payments: List[Dict[str, Any]] = []
        self.progress_updates: List[Dict[str, Any]] = []
        self.inspections: List[Dict[str, Any]] = []
        self.sanctions: List[Dict[str, Any]] = []
        self.estimates: List[Dict[str, Any]] = []
        self.assets: List[Dict[str, Any]] = []

    def _reset(self, seed: Optional[int] = None) -> None:
        if seed is not None:
            self.seed = seed
        self.rng = random.Random(self.seed)
        self.agencies = []
        self.works = []
        self.payments = []
        self.progress_updates = []
        self.inspections = []
        self.sanctions = []
        self.estimates = []
        self.assets = []

    def generate_agencies(self, min_count: int = 260) -> List[Dict[str, Any]]:
        """
        Generates at least 250+ distinct synthetic agencies across states and districts.
        """
        agency_types = [
            "Public Works Dept (Demo)",
            "Rural Development Agency (Demo)",
            "Municipal Engineering Cell (Demo)",
            "Water Supply & Sanitation Board (Demo)",
            "Zilla Parishad Engineering Division (Demo)",
            "State Renewable Energy Development Corp (Demo)",
            "Irrigation & Flood Management Dept (Demo)",
            "State Sports Infrastructure Authority (Demo)",
        ]

        agencies: List[Dict[str, Any]] = []
        all_districts = []
        for state, d_dict in STATE_DISTRICT_MASTER.items():
            for dist in d_dict.keys():
                all_districts.append((state, dist))

        count = 0
        while len(agencies) < min_count:
            state, district = self.rng.choice(all_districts)
            a_type = self.rng.choice(agency_types)
            count += 1
            agency_id = f"AGY-SYNTH-{count:04d}"
            agency_name = f"{district} {a_type} Unit-{((count - 1) % 5) + 1}"
            
            nodal_officer = f"Nodal Officer (Demo Code {count:03d})"
            email = f"officer.demo.{count:04d}@{district.lower().replace(' ', '')}.synthetic.gov.in"
            rating = round(self.rng.uniform(3.2, 4.9), 2)
            status = "Active" if self.rng.random() > 0.05 else "Suspended (Demo)"

            rec = AgencyRecord(
                agency_id=agency_id,
                agency_name=agency_name,
                agency_type=a_type,
                state=state,
                district=district,
                nodal_officer_designation=nodal_officer,
                contact_email_synthetic=email,
                performance_rating=rating,
                active_status=status,
                synthetic_demo_data=SYNTHETIC_FLAG,
            ).to_dict()
            agencies.append(rec)

        self.agencies = agencies
        return agencies

    def _generate_title(self, category: str, district: str, sub_divisions: List[str]) -> str:
        templates = TITLE_TEMPLATES.get(category, TITLE_TEMPLATES["Community Infrastructure & Halls"])
        template = self.rng.choice(templates)
        
        loc1 = f"{self.rng.choice(sub_divisions)} Sector-{self.rng.randint(1, 15)}"
        loc2 = f"{self.rng.choice(sub_divisions)} Village-{self.rng.randint(1, 25)}"
        
        return template.format(
            location=loc1,
            village=loc2,
            loc_a=loc1,
            loc_b=loc2,
            school_loc=loc1,
        )

    def _generate_coordinates(self, base_lat: float, base_lon: float) -> Tuple[float, float]:
        # Add slight jitter within ~10km radius
        jitter_lat = (self.rng.random() - 0.5) * 0.15
        jitter_lon = (self.rng.random() - 0.5) * 0.15
        return round(base_lat + jitter_lat, 6), round(base_lon + jitter_lon, 6)

    def generate_all(
        self,
        num_works: int = 10000,
        is_dirty: bool = False,
        anomaly_rate: float = 0.08,
        min_agencies: int = 260,
    ) -> Dict[str, Any]:
        """
        Generates full relational data collection:
        Works, Payments (>= 30k), Progress Updates (>= 40k), Agencies (>= 250),
        Sanctions, Estimates, Inspections, Assets, and Unified table.
        """
        self._reset()
        self.generate_agencies(min_count=min_agencies)

        # Pre-assign MP references per state/constituency
        mp_directory: Dict[str, Dict[str, str]] = {}
        mp_counter = 1
        for state, d_dict in STATE_DISTRICT_MASTER.items():
            for district, d_info in d_dict.items():
                const = d_info["constituency"]
                if const not in mp_directory:
                    is_lok_sabha = (mp_counter % 6 != 0)
                    house = "Lok Sabha (Demo)" if is_lok_sabha else "Rajya Sabha (Demo)"
                    ref_prefix = "MP-LOK-DEMO" if is_lok_sabha else "MP-RAJ-DEMO"
                    mp_directory[const] = {
                        "mp_reference": f"{ref_prefix}-{mp_counter:03d}",
                        "mp_house": house,
                    }
                    mp_counter += 1

        all_state_districts = []
        for state, d_dict in STATE_DISTRICT_MASTER.items():
            for dist, info in d_dict.items():
                all_state_districts.append((state, dist, info))

        base_start_date = datetime(2022, 4, 1)
        base_end_date = datetime(2026, 2, 1)
        total_days = (base_end_date - base_start_date).days

        payment_id_counter = 1
        progress_id_counter = 1
        inspection_id_counter = 1
        estimate_id_counter = 1
        sanction_id_counter = 1
        asset_id_counter = 1

        works_to_generate = num_works
        # If dirty, we will inject anomalies into a subset
        num_anomalous = int(works_to_generate * anomaly_rate) if is_dirty else 0
        anomaly_indices = set(self.rng.sample(range(works_to_generate), num_anomalous)) if is_dirty else set()

        duplicate_candidates: List[Dict[str, Any]] = []

        for i in range(works_to_generate):
            work_idx = i + 1
            work_id = f"MPLAD-WRK-{work_idx:06d}"
            state, district, d_info = self.rng.choice(all_state_districts)
            constituency = d_info["constituency"]
            mp_info = mp_directory[constituency]
            mp_ref = mp_info["mp_reference"]
            mp_house = mp_info["mp_house"]
            
            category = self.rng.choice(CATEGORIES)
            title = self._generate_title(category, district, d_info["sub_divisions"])
            
            # Select agency in same state/district or fallback
            matching_agencies = [a for a in self.agencies if a["district"] == district]
            if not matching_agencies:
                matching_agencies = self.agencies
            agency = self.rng.choice(matching_agencies)
            
            # Financials
            benchmark = CATEGORY_BENCHMARKS[category]
            # Log-normal distribution centered near median
            mean_log = math.log(benchmark["median_cost"])
            raw_cost = math.exp(self.rng.gauss(mean_log, 0.45))
            est_cost = round(min(max(raw_cost, benchmark["min_cost"]), benchmark["max_cost"]), 2)
            # Sanction usually 95-102% of estimate
            sanction_cost = round(est_cost * self.rng.uniform(0.95, 1.02), 2)
            
            # Dates
            rec_days = self.rng.randint(0, total_days - 365)
            rec_date = base_start_date + timedelta(days=rec_days)
            sanction_days = self.rng.randint(15, 60)
            sanction_date = rec_date + timedelta(days=sanction_days)
            wo_days = self.rng.randint(10, 45)
            wo_date = sanction_date + timedelta(days=wo_days)
            commence_days = self.rng.randint(10, 30)
            commence_date = wo_date + timedelta(days=commence_days)
            target_days = benchmark["typical_duration_days"] + self.rng.randint(-30, 90)
            target_date = commence_date + timedelta(days=target_days)
            
            # Status distribution:
            # ~45% Completed, ~35% In Progress, ~10% Work Order, ~5% Sanctioned, ~3% Recommended, ~2% Stalled
            rand_status = self.rng.random()
            if rand_status < 0.45:
                status = STATUS_COMPLETED
                progress_pct = 100.0
                actual_comp_days = self.rng.randint(-20, 60)
                actual_comp_date = target_date + timedelta(days=actual_comp_days)
                if actual_comp_date > datetime(2026, 2, 28):
                    actual_comp_date = datetime(2026, 2, 20)
            elif rand_status < 0.80:
                status = STATUS_IN_PROGRESS
                progress_pct = round(self.rng.uniform(15.0, 92.0), 1)
                actual_comp_date = None
            elif rand_status < 0.90:
                status = STATUS_WORK_ORDER
                progress_pct = 0.0
                actual_comp_date = None
            elif rand_status < 0.95:
                status = STATUS_SANCTIONED
                progress_pct = 0.0
                actual_comp_date = None
            elif rand_status < 0.98:
                status = STATUS_RECOMMENDED
                progress_pct = 0.0
                sanction_date = None
                wo_date = None
                commence_date = None
                target_date = None
                actual_comp_date = None
            else:
                status = STATUS_STALLED
                progress_pct = round(self.rng.uniform(10.0, 45.0), 1)
                actual_comp_date = None

            # Calculate payments and expenditure according to status and progress
            if status == STATUS_RECOMMENDED:
                cumulative_pay = 0.0
                expenditure = 0.0
                num_payments = 0
                num_updates = 0
            elif status == STATUS_SANCTIONED:
                cumulative_pay = 0.0
                expenditure = 0.0
                num_payments = 0
                num_updates = 0
            elif status == STATUS_WORK_ORDER:
                # Up to 1 mobilization advance payment
                cumulative_pay = round(sanction_cost * 0.15, 2) if self.rng.random() > 0.5 else 0.0
                expenditure = round(cumulative_pay * 0.5, 2)
                num_payments = 1 if cumulative_pay > 0 else 0
                num_updates = 1
            elif status == STATUS_IN_PROGRESS:
                # Payments roughly match or slightly lead progress
                pay_ratio = min(1.0, (progress_pct / 100.0) + self.rng.uniform(-0.05, 0.10))
                cumulative_pay = round(sanction_cost * max(0.20, pay_ratio), 2)
                expenditure = round(cumulative_pay * self.rng.uniform(0.85, 0.98), 2)
                num_payments = self.rng.randint(2, 5)
                num_updates = self.rng.randint(3, 6)
            elif status == STATUS_COMPLETED:
                cumulative_pay = sanction_cost
                expenditure = round(sanction_cost * self.rng.uniform(0.97, 1.0), 2)
                num_payments = self.rng.randint(3, 6)
                num_updates = self.rng.randint(4, 7)
            else:  # STALLED
                pay_ratio = max(0.3, (progress_pct / 100.0) + self.rng.uniform(0.1, 0.3))
                cumulative_pay = round(sanction_cost * min(1.0, pay_ratio), 2)
                expenditure = round(cumulative_pay * 0.8, 2)
                num_payments = self.rng.randint(2, 4)
                num_updates = self.rng.randint(2, 5)


            lat, lon = self._generate_coordinates(d_info["lat"], d_info["lon"])

            work_record = {
                "work_id": work_id,
                "state": state,
                "district": district,
                "constituency": constituency,
                "mp_reference": mp_ref,
                "mp_house": mp_house,
                "work_title": title,
                "category": category,
                "agency_id": agency["agency_id"],
                "agency_name": agency["agency_name"],
                "status": status,
                "estimate_amount": est_cost,
                "sanctioned_amount": sanction_cost if status != STATUS_RECOMMENDED else 0.0,
                "cumulative_payments": cumulative_pay,
                "expenditure": expenditure,
                "physical_progress_pct": progress_pct,
                "recommendation_date": rec_date.strftime("%Y-%m-%d"),
                "sanction_date": sanction_date.strftime("%Y-%m-%d") if sanction_date else None,
                "work_order_date": wo_date.strftime("%Y-%m-%d") if wo_date else None,
                "commencement_date": commence_date.strftime("%Y-%m-%d") if commence_date else None,
                "target_completion_date": target_date.strftime("%Y-%m-%d") if target_date else None,
                "actual_completion_date": actual_comp_date.strftime("%Y-%m-%d") if actual_comp_date else None,
                "latitude": lat,
                "longitude": lon,
                "is_anomaly": False,
                "anomaly_type": None,
                "anomaly_description": None,
                "duplicate_of_work_id": None,
                "synthetic_demo_data": SYNTHETIC_FLAG,
            }

            # Generate relational Estimate
            est_record = EstimateRecord(
                estimate_id=f"EST-DEMO-{estimate_id_counter:06d}",
                work_id=work_id,
                prepared_date=rec_date.strftime("%Y-%m-%d"),
                technical_sanction_date=sanction_date.strftime("%Y-%m-%d") if sanction_date else None,
                estimated_amount=est_cost,
                contingency_pct=round(self.rng.uniform(2.0, 5.0), 1),
                schedule_of_rates_year=2023,
                technical_authority=f"Superintending Engineer ({district} Demo)",
                synthetic_demo_data=SYNTHETIC_FLAG,
            ).to_dict()
            self.estimates.append(est_record)
            estimate_id_counter += 1

            # Generate relational Sanction if applicable
            if status != STATUS_RECOMMENDED and sanction_date:
                sanc_record = SanctionRecord(
                    sanction_id=f"SANC-DEMO-{sanction_id_counter:06d}",
                    work_id=work_id,
                    sanction_order_number=f"MPLAD/{district[:3].upper()}/{sanction_date.year}/{sanction_id_counter:05d}",
                    sanction_date=sanction_date.strftime("%Y-%m-%d"),
                    sanctioned_amount=sanction_cost,
                    installment_schedule="40-40-20" if sanction_cost > 1000000 else "50-50",
                    approving_authority=f"District Collector & Magistrate ({district} Demo)",
                    synthetic_demo_data=SYNTHETIC_FLAG,
                ).to_dict()
                self.sanctions.append(sanc_record)
                sanction_id_counter += 1

            # Generate relational Payments
            work_payments: List[Dict[str, Any]] = []
            if num_payments > 0 and cumulative_pay > 0 and sanction_date:
                remaining_pay = cumulative_pay
                pay_start = sanction_date + timedelta(days=15)
                for p_num in range(1, num_payments + 1):
                    if p_num == num_payments:
                        p_amt = round(remaining_pay, 2)
                    else:
                        chunk = cumulative_pay / num_payments
                        p_amt = round(chunk * self.rng.uniform(0.85, 1.15), 2)
                        p_amt = min(p_amt, remaining_pay)
                        remaining_pay -= p_amt

                    p_date = pay_start + timedelta(days=(p_num - 1) * 45 + self.rng.randint(5, 20))
                    p_rec = PaymentRecord(
                        payment_id=f"PAY-DEMO-{payment_id_counter:07d}",
                        work_id=work_id,
                        installment_number=p_num,
                        payment_date=p_date.strftime("%Y-%m-%d"),
                        amount=p_amt,
                        voucher_number=f"VR-DEMO-{p_date.year}-{payment_id_counter:06d}",
                        payee_agency_id=agency["agency_id"],
                        disbursement_mode="PFMS_DEMO_TRANSFER",
                        payment_status="Disbursed",
                        synthetic_demo_data=SYNTHETIC_FLAG,
                    ).to_dict()
                    work_payments.append(p_rec)
                    self.payments.append(p_rec)
                    payment_id_counter += 1

            # Generate relational Progress Updates
            work_updates: List[Dict[str, Any]] = []
            if num_updates > 0 and commence_date:
                stages = ["Planning & Mobilization", "Excavation & Foundation", "Structural Construction", "Finishing & Installations", "Testing & Commissioning", "Final Handover"]
                curr_progress = 0.0
                curr_exp = 0.0
                for u_num in range(1, num_updates + 1):
                    stage_target = (progress_pct / num_updates) * u_num
                    curr_progress = round(stage_target * self.rng.uniform(0.9, 1.05), 1)
                    if u_num == num_updates:
                        curr_progress = progress_pct
                    curr_progress = min(100.0, max(0.0, curr_progress))
                    curr_exp = round((expenditure / num_updates) * u_num, 2)

                    u_date = commence_date + timedelta(days=(u_num - 1) * 35 + self.rng.randint(5, 15))
                    stage_name = stages[min(u_num - 1, len(stages) - 1)]
                    photo_ref = f"photos/synth_work_{work_id}_stage_{u_num}.jpg" if curr_progress > 0 else None

                    u_rec = ProgressUpdateRecord(
                        update_id=f"UPD-DEMO-{progress_id_counter:07d}",
                        work_id=work_id,
                        update_date=u_date.strftime("%Y-%m-%d"),
                        physical_progress_pct=curr_progress,
                        stage_name=stage_name,
                        expenditure_to_date=curr_exp,
                        reported_by_designation=f"Junior Engineer ({agency['agency_name']})",
                        remarks=f"Stage '{stage_name}' executed. Physical progress at {curr_progress}%.",
                        geo_tagged_photo_ref=photo_ref,
                        synthetic_demo_data=SYNTHETIC_FLAG,
                    ).to_dict()
                    work_updates.append(u_rec)
                    self.progress_updates.append(u_rec)
                    progress_id_counter += 1

            # Generate Inspections
            work_inspections: List[Dict[str, Any]] = []
            if status in [STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_STALLED] and commence_date:
                insp_count = 1 if status != STATUS_COMPLETED else self.rng.randint(1, 3)
                for insp_idx in range(insp_count):
                    insp_date = commence_date + timedelta(days=insp_idx * 60 + self.rng.randint(20, 50))
                    rating = self.rng.choice(INSPECTION_RATINGS[:3]) if status != STATUS_STALLED else "Requires Rectification"
                    defects = rating in ["Requires Rectification", "Non-Compliant"]

                    insp_rec = InspectionRecord(
                        inspection_id=f"INSP-DEMO-{inspection_id_counter:06d}",
                        work_id=work_id,
                        inspection_date=insp_date.strftime("%Y-%m-%d"),
                        inspector_designation=self.rng.choice(INSPECTOR_DESIGNATIONS),
                        inspection_stage="Interim Progress Inspection" if insp_idx < insp_count - 1 else "Final Quality Inspection",
                        rating=rating,
                        findings_summary=f"Site inspection conducted. Quality benchmark verified as {rating}.",
                        defects_observed=defects,
                        rectification_deadline=(insp_date + timedelta(days=30)).strftime("%Y-%m-%d") if defects else None,
                        inspection_photo_ref=f"inspections/insp_demo_{inspection_id_counter:06d}.jpg",
                        synthetic_demo_data=SYNTHETIC_FLAG,
                    ).to_dict()
                    work_inspections.append(insp_rec)
                    self.inspections.append(insp_rec)
                    inspection_id_counter += 1

            # Generate Asset Record if completed
            work_assets: List[Dict[str, Any]] = []
            if status == STATUS_COMPLETED and actual_comp_date:
                asset_rec = AssetRecord(
                    asset_id=f"AST-DEMO-{asset_id_counter:06d}",
                    work_id=work_id,
                    asset_name=f"{category} Asset - {title[:40]}",
                    category=category,
                    location_description=f"{district}, {state}",
                    latitude=lat,
                    longitude=lon,
                    handover_date=actual_comp_date.strftime("%Y-%m-%d"),
                    custodian_department=f"{district} Local Panchayat / Municipal Body (Demo)",
                    maintenance_status="Operational",
                    synthetic_demo_data=SYNTHETIC_FLAG,
                ).to_dict()
                work_assets.append(asset_rec)
                self.assets.append(asset_rec)
                asset_id_counter += 1

            # Save clean work record
            self.works.append(work_record)
            if not is_dirty:
                duplicate_candidates.append(work_record)

        # If dirty, inject labelled anomalies and data quality issues into selected works
        if is_dirty and num_anomalous > 0:
            self._inject_dirty_anomalies_and_issues(anomaly_indices)

        return {
            "works": self.works,
            "payments": self.payments,
            "progress_updates": self.progress_updates,
            "agencies": self.agencies,
            "inspections": self.inspections,
            "sanctions": self.sanctions,
            "estimates": self.estimates,
            "assets": self.assets,
        }

    def _inject_dirty_anomalies_and_issues(self, anomaly_indices: set) -> None:
        """
        Injects the 5 demonstration scenarios + standard data-quality issues into the dirty dataset.
        """
        indices_list = list(anomaly_indices)
        self.rng.shuffle(indices_list)
        
        # Partition indices among anomaly types
        n = len(indices_list)
        n_mismatch = int(n * 0.20)
        n_outlier = int(n * 0.20)
        n_stalled = int(n * 0.15)
        n_duplicate = int(n * 0.15)
        n_missing_ev = int(n * 0.15)
        # Remaining will receive standard data-quality issues
        
        idx_mismatch = indices_list[:n_mismatch]
        idx_outlier = indices_list[n_mismatch : n_mismatch + n_outlier]
        idx_stalled = indices_list[n_mismatch + n_outlier : n_mismatch + n_outlier + n_stalled]
        idx_dup = indices_list[n_mismatch + n_outlier + n_stalled : n_mismatch + n_outlier + n_stalled + n_duplicate]
        idx_missing_ev = indices_list[n_mismatch + n_outlier + n_stalled + n_duplicate : n_mismatch + n_outlier + n_stalled + n_duplicate + n_missing_ev]
        idx_dq_issues = indices_list[n_mismatch + n_outlier + n_stalled + n_duplicate + n_missing_ev :]

        # 1. Payment-Progress Mismatches
        for idx in idx_mismatch:
            work = self.works[idx]
            w_payments = [p for p in self.payments if p["work_id"] == work["work_id"]]
            w_updates = [u for u in self.progress_updates if u["work_id"] == work["work_id"]]
            inject_payment_progress_mismatch(work, w_payments, w_updates, self.rng)

        # 2. Cost Outliers
        for idx in idx_outlier:
            work = self.works[idx]
            inject_cost_outlier(work, self.rng)

        # 3. Stalled Works
        for idx in idx_stalled:
            work = self.works[idx]
            w_updates = [u for u in self.progress_updates if u["work_id"] == work["work_id"]]
            inject_stalled_work(work, w_updates, self.rng)

        # 4. Possible Duplicates
        for idx in idx_dup:
            target_work = self.works[idx]
            # Pick a clean work to clone from
            clean_source_idx = (idx + 50) % len(self.works)
            if clean_source_idx in anomaly_indices:
                clean_source_idx = (clean_source_idx + 137) % len(self.works)
            source_work = self.works[clean_source_idx]
            dup_rec = create_duplicate_work_record(source_work, target_work["work_id"], self.rng)
            self.works[idx] = dup_rec

        # 5. Missing Completion Evidence
        for idx in idx_missing_ev:
            work = self.works[idx]
            w_inspections = [i for i in self.inspections if i["work_id"] == work["work_id"]]
            w_assets = [a for a in self.assets if a["work_id"] == work["work_id"]]
            inject_missing_completion_evidence(work, w_inspections, w_assets, self.rng)
            # Filter them out of generator lists
            self.inspections = [i for i in self.inspections if i["work_id"] != work["work_id"]]
            self.assets = [a for a in self.assets if a["work_id"] != work["work_id"]]

        # 6. Data Quality Issues (missing IDs, negative amounts, payments > sanction, invalid dates, out of bounds lat/lon, mismatched state/districts)
        dq_issue_types = [
            "NEGATIVE_AMOUNT",
            "PAYMENTS_EXCEED_SANCTION",
            "INVALID_DATE_ORDER",
            "PROGRESS_ABOVE_100",
            "INVALID_STATE_DISTRICT_LINK",
            "COORDINATES_OUT_OF_BOUNDS",
            "MISSING_WORK_ID",
        ]

        for i, idx in enumerate(idx_dq_issues):
            work = self.works[idx]
            dq_type = dq_issue_types[i % len(dq_issue_types)]
            work["is_anomaly"] = True
            work["anomaly_type"] = AnomalyType.DATA_QUALITY_ISSUE

            if dq_type == "NEGATIVE_AMOUNT":
                work["sanctioned_amount"] = -abs(work["sanctioned_amount"] or 500000.0)
                work["anomaly_description"] = "Data quality issue: Negative sanctioned amount."
            elif dq_type == "PAYMENTS_EXCEED_SANCTION":
                work["cumulative_payments"] = round(work["sanctioned_amount"] * 1.45, 2)
                work["anomaly_description"] = "Compliance rule violation: Cumulative payments exceed sanctioned budget by 45%."
            elif dq_type == "INVALID_DATE_ORDER":
                # Completion before sanction date
                work["sanction_date"] = "2025-06-01"
                work["actual_completion_date"] = "2024-01-15"
                work["anomaly_description"] = "Data quality issue: Completion date precedes sanction date."
            elif dq_type == "PROGRESS_ABOVE_100":
                work["physical_progress_pct"] = 135.0
                work["anomaly_description"] = "Data quality issue: Physical progress percentage exceeds 100% (135.0%)."
            elif dq_type == "INVALID_STATE_DISTRICT_LINK":
                work["state"] = "Tamil Nadu"
                work["district"] = "Nagpur"  # Nagpur is in Maharashtra
                work["anomaly_description"] = "Data quality issue: District 'Nagpur' does not exist in State 'Tamil Nadu'."
            elif dq_type == "COORDINATES_OUT_OF_BOUNDS":
                work["latitude"] = 78.50  # Swapped coordinates
                work["longitude"] = 12.30
                work["anomaly_description"] = "Data quality issue: Geographic latitude (78.50) is out of India bounding bounds."
            elif dq_type == "MISSING_WORK_ID":
                work["work_id"] = ""
                work["anomaly_description"] = "Data quality issue: Mandatory primary key 'work_id' is missing/empty."

    def build_unified_records(self) -> List[Dict[str, Any]]:
        """
        Creates a unified flattened master table representation combining works with
        aggregated inspection metrics, payment counts, and progress update counts.
        """
        # Build lookup maps for performance
        payments_by_work: Dict[str, List[Dict[str, Any]]] = {}
        for p in self.payments:
            payments_by_work.setdefault(p["work_id"], []).append(p)

        updates_by_work: Dict[str, List[Dict[str, Any]]] = {}
        for u in self.progress_updates:
            updates_by_work.setdefault(u["work_id"], []).append(u)

        inspections_by_work: Dict[str, List[Dict[str, Any]]] = {}
        for insp in self.inspections:
            inspections_by_work.setdefault(insp["work_id"], []).append(insp)

        unified_list: List[Dict[str, Any]] = []
        for w in self.works:
            wid = w.get("work_id", "")
            w_pays = payments_by_work.get(wid, [])
            w_ups = updates_by_work.get(wid, [])
            w_insps = inspections_by_work.get(wid, [])

            latest_insp = w_insps[-1] if w_insps else None

            rec = UnifiedWorkDemoRecord(
                work_id=w.get("work_id", ""),
                state=w.get("state", ""),
                district=w.get("district", ""),
                constituency=w.get("constituency", ""),
                mp_reference=w.get("mp_reference", ""),
                mp_house=w.get("mp_house", ""),
                work_title=w.get("work_title", ""),
                category=w.get("category", ""),
                agency_id=w.get("agency_id", ""),
                agency_name=w.get("agency_name", ""),
                status=w.get("status", ""),
                estimate_amount=w.get("estimate_amount", 0.0),
                sanctioned_amount=w.get("sanctioned_amount", 0.0),
                cumulative_payments=w.get("cumulative_payments", 0.0),
                expenditure=w.get("expenditure", 0.0),
                physical_progress_pct=w.get("physical_progress_pct", 0.0),
                recommendation_date=w.get("recommendation_date", ""),
                sanction_date=w.get("sanction_date"),
                work_order_date=w.get("work_order_date"),
                commencement_date=w.get("commencement_date"),
                target_completion_date=w.get("target_completion_date"),
                actual_completion_date=w.get("actual_completion_date"),
                latitude=w.get("latitude"),
                longitude=w.get("longitude"),
                latest_inspection_date=latest_insp["inspection_date"] if latest_insp else None,
                latest_inspection_rating=latest_insp["rating"] if latest_insp else None,
                latest_inspector_designation=latest_insp["inspector_designation"] if latest_insp else None,
                inspection_count=len(w_insps),
                payment_count=len(w_pays),
                progress_update_count=len(w_ups),
                is_anomaly=w.get("is_anomaly", False),
                anomaly_type=w.get("anomaly_type"),
                anomaly_description=w.get("anomaly_description"),
                duplicate_of_work_id=w.get("duplicate_of_work_id"),
                synthetic_demo_data=SYNTHETIC_FLAG,
            ).to_dict()
            unified_list.append(rec)

        return unified_list
