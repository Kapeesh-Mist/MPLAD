"""
Anomaly Injection and Demonstration Scenario Generators for MPLADS Synthetic Data Engine.
Provides deterministic scenario generators with explicit ground-truth labelling.
"""

from typing import Dict, List, Tuple, Any, Optional
import random
from datetime import datetime, timedelta

try:
    from .constants import (
        CATEGORIES,
        CATEGORY_BENCHMARKS,
        STATUS_COMPLETED,
        STATUS_IN_PROGRESS,
        STATUS_STALLED,
        format_inr,
        format_inr_words,
    )
    from .schemas import WorkRecord, PaymentRecord, ProgressUpdateRecord, InspectionRecord, AssetRecord
except (ImportError, ValueError):
    from constants import (
        CATEGORIES,
        CATEGORY_BENCHMARKS,
        STATUS_COMPLETED,
        STATUS_IN_PROGRESS,
        STATUS_STALLED,
        format_inr,
        format_inr_words,
    )
    from schemas import WorkRecord, PaymentRecord, ProgressUpdateRecord, InspectionRecord, AssetRecord



class AnomalyType:
    PAYMENT_PROGRESS_MISMATCH = "PAYMENT_PROGRESS_MISMATCH"
    COST_OUTLIER = "COST_OUTLIER"
    STALLED_WORK = "STALLED_WORK"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
    MISSING_COMPLETION_EVIDENCE = "MISSING_COMPLETION_EVIDENCE"
    DATA_QUALITY_ISSUE = "DATA_QUALITY_ISSUE"


def inject_payment_progress_mismatch(
    work: Dict[str, Any],
    payments: List[Dict[str, Any]],
    progress_updates: List[Dict[str, Any]],
    rng: random.Random
) -> None:
    """
    Scenario 1: Payment-Progress Mismatch
    Disburses 80-100% of sanctioned funds while physical progress remains stalled at 10-25%.
    """
    sanctioned = work["sanctioned_amount"]
    mismatch_pay_pct = rng.uniform(0.80, 1.0)
    total_paid = round(sanctioned * mismatch_pay_pct, 2)
    work["cumulative_payments"] = total_paid
    work["expenditure"] = round(total_paid * rng.uniform(0.9, 1.0), 2)
    
    # Force low physical progress
    low_progress = round(rng.uniform(5.0, 25.0), 1)
    work["physical_progress_pct"] = low_progress
    work["status"] = STATUS_IN_PROGRESS
    
    # Adjust progress updates to reflect low progress
    if progress_updates:
        for u in progress_updates:
            u["physical_progress_pct"] = min(u["physical_progress_pct"], low_progress)
            u["expenditure_to_date"] = min(u["expenditure_to_date"], work["expenditure"])
        progress_updates[-1]["physical_progress_pct"] = low_progress
    
    # Ensure payments reflect high disbursement
    if payments:
        per_payment = total_paid / len(payments)
        for p in payments:
            p["amount"] = round(per_payment, 2)
    
    work["is_anomaly"] = True
    work["anomaly_type"] = AnomalyType.PAYMENT_PROGRESS_MISMATCH
    work["anomaly_description"] = (
        f"Severe financial-physical divergence: {round(mismatch_pay_pct*100, 1)}% of sanctioned funds "
        f"({format_inr(total_paid)}) disbursed while physical progress is only {low_progress}%."
    )


def inject_cost_outlier(
    work: Dict[str, Any],
    rng: random.Random
) -> None:
    """
    Scenario 2: Cost Outlier
    Scales estimate and sanctioned amounts to 4x - 9x the category median benchmark.
    """
    category = work["category"]
    benchmark = CATEGORY_BENCHMARKS.get(category, CATEGORY_BENCHMARKS["Community Infrastructure & Halls"])
    multiplier = round(rng.uniform(4.0, 8.5), 2)
    
    inflated_estimate = round(benchmark["median_cost"] * multiplier, 2)
    inflated_sanction = round(inflated_estimate * rng.uniform(0.95, 1.05), 2)
    
    work["estimate_amount"] = inflated_estimate
    work["sanctioned_amount"] = inflated_sanction
    
    # Adjust payments if work was in progress or completed
    if work["cumulative_payments"] > 0:
        ratio = work["cumulative_payments"] / max(1.0, work["sanctioned_amount"])
        work["cumulative_payments"] = round(inflated_sanction * min(1.0, ratio), 2)
        work["expenditure"] = round(work["cumulative_payments"] * 0.95, 2)
        
    work["is_anomaly"] = True
    work["anomaly_type"] = AnomalyType.COST_OUTLIER
    work["anomaly_description"] = (
        f"Cost outlier: Sanctioned amount of {format_inr(inflated_sanction)} ({format_inr_words(inflated_sanction)}) is {multiplier:.1f}x higher "
        f"than standard category median benchmark of {format_inr(benchmark['median_cost'])} ({format_inr_words(benchmark['median_cost'])}) for '{category}'."
    )



def inject_stalled_work(
    work: Dict[str, Any],
    progress_updates: List[Dict[str, Any]],
    rng: random.Random
) -> None:
    """
    Scenario 3: Stalled Work
    Work commenced in the past, target completion date elapsed >180 days ago,
    no recent progress updates, progress stuck at 20-50%.
    """
    work["status"] = STATUS_STALLED
    stalled_progress = round(rng.uniform(20.0, 48.0), 1)
    work["physical_progress_pct"] = stalled_progress
    work["actual_completion_date"] = None
    
    # Manipulate dates to show stall
    base_date = datetime.strptime(work["recommendation_date"], "%Y-%m-%d")
    sanction_d = base_date + timedelta(days=rng.randint(30, 60))
    commence_d = sanction_d + timedelta(days=rng.randint(30, 60))
    target_d = commence_d + timedelta(days=rng.randint(120, 200))
    
    work["sanction_date"] = sanction_d.strftime("%Y-%m-%d")
    work["commencement_date"] = commence_d.strftime("%Y-%m-%d")
    work["target_completion_date"] = target_d.strftime("%Y-%m-%d")
    
    # Last update was long ago
    if progress_updates:
        last_update_d = commence_d + timedelta(days=rng.randint(30, 90))
        progress_updates[-1]["update_date"] = last_update_d.strftime("%Y-%m-%d")
        progress_updates[-1]["physical_progress_pct"] = stalled_progress
        progress_updates[-1]["remarks"] = "Work stalled due to administrative and contractor site delays (Demo flag)."
        
    work["is_anomaly"] = True
    work["anomaly_type"] = AnomalyType.STALLED_WORK
    work["anomaly_description"] = (
        f"Stalled project: Target completion date ({work['target_completion_date']}) elapsed with progress "
        f"stuck at {stalled_progress}% and no physical updates for over 200 days."
    )


def create_duplicate_work_record(
    source_work: Dict[str, Any],
    new_work_id: str,
    rng: random.Random
) -> Dict[str, Any]:
    """
    Scenario 4: Possible Duplicate Work
    Creates a new work record that duplicates a source work's location, category, and scope
    with minor variations in title phrasing or date offsets.
    """
    dup = dict(source_work)
    dup["work_id"] = new_work_id
    
    # Slight title variations (rephrasing or synonym substitution)
    title = source_work["work_title"]
    variations = [
        title,  # Exact duplicate
        title.replace("Construction of", "Erection of"),
        title.replace("Installation of", "Setting up of"),
        title.replace("Provision of", "Supply and Installation of"),
        title + " (Phase-I)",
        title.replace("at ", "in "),
    ]
    dup["work_title"] = rng.choice(variations)
    
    # Cost may be identical or within 2%
    cost_variation = rng.uniform(0.98, 1.02)
    dup["estimate_amount"] = round(source_work["estimate_amount"] * cost_variation, 2)
    dup["sanctioned_amount"] = round(source_work["sanctioned_amount"] * cost_variation, 2)
    dup["cumulative_payments"] = round(source_work["cumulative_payments"] * cost_variation, 2)
    dup["expenditure"] = round(source_work["expenditure"] * cost_variation, 2)
    
    dup["is_anomaly"] = True
    dup["anomaly_type"] = AnomalyType.POSSIBLE_DUPLICATE
    dup["duplicate_of_work_id"] = source_work["work_id"]
    dup["anomaly_description"] = (
        f"Potential duplicate recommendation: Highly similar scope and title matching work {source_work['work_id']} "
        f"in district {source_work['district']}, category '{source_work['category']}'."
    )
    return dup


def inject_missing_completion_evidence(
    work: Dict[str, Any],
    inspections: List[Dict[str, Any]],
    assets: List[Dict[str, Any]],
    rng: random.Random
) -> None:
    """
    Scenario 5: Missing Completion Evidence
    Work marked Completed and 100% paid, but lacks actual completion date,
    final inspection sign-off, or physical asset registration.
    """
    work["status"] = STATUS_COMPLETED
    work["physical_progress_pct"] = 100.0
    work["cumulative_payments"] = work["sanctioned_amount"]
    work["expenditure"] = work["sanctioned_amount"]
    
    # Strip completion evidence
    work["actual_completion_date"] = None  # Missing completion date
    
    # Clear out inspections or mark them unverified
    inspections.clear()
    
    # Clear out or remove asset handover
    assets.clear()
    
    work["is_anomaly"] = True
    work["anomaly_type"] = AnomalyType.MISSING_COMPLETION_EVIDENCE
    work["anomaly_description"] = (
        "Incomplete closure documentation: Work marked as 100% completed with full financial disbursement, "
        "but lacks mandatory actual completion date, completion inspection sign-off, and asset register record."
    )
