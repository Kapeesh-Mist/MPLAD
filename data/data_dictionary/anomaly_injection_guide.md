# MPLADS Synthetic Anomaly Injection & Demonstration Catalog

> [!NOTE]
> **Data Quality & Compliance Framework**: All injected anomalies in the synthetic dataset represent controlled edge cases and demonstration scenarios designed for benchmarking risk scoring models, rule engines, and audit dashboards. Data inconsistencies are categorized as data quality or compliance gaps, not criminal fraud allegations.

---

## 1. Catalog of Demonstration Scenarios

| Scenario Code | Demonstration Scenario | Core Pattern | Ground-Truth Flags | Target AI / Rule Detector |
| :--- | :--- | :--- | :--- | :--- |
| `PAYMENT_PROGRESS_MISMATCH` | **Payment-Progress Mismatch** | High financial disbursement ($80\% - 100\%$) released while physical progress is stalled ($< 25\%$). | `is_anomaly=True`<br>`anomaly_type="PAYMENT_PROGRESS_MISMATCH"` | `ai_module/anomaly/payment_progress_mismatch.py` |
| `COST_OUTLIER` | **Cost Outlier** | Sanctioned or estimate amount is $4\times - 8.5\times$ higher than category median benchmark for the district/sector. | `is_anomaly=True`<br>`anomaly_type="COST_OUTLIER"` | `ai_module/anomaly/cost_outlier.py` |
| `STALLED_WORK` | **Stalled / Delayed Work** | Project commenced with target completion date passed by $>180$ days, no progress reports filed for $>180$ days, progress stuck at $20-48\%$. | `is_anomaly=True`<br>`anomaly_type="STALLED_WORK"` | `ai_module/rules/compliance_rules.py` |
| `POSSIBLE_DUPLICATE` | **Possible Duplicate Work** | Near-identical project scope, category, location, and cost recommended under duplicate or overlapping records. | `is_anomaly=True`<br>`anomaly_type="POSSIBLE_DUPLICATE"`<br>`duplicate_of_work_id="MPLAD-WRK-XXXX"` | `ai_module/similarity/duplicate_detection.py` |
| `MISSING_COMPLETION_EVIDENCE` | **Missing Completion Evidence** | Work status recorded as 'Completed' with $100\%$ disbursement, but lacking completion certificate date or final inspection sign-off. | `is_anomaly=True`<br>`anomaly_type="MISSING_COMPLETION_EVIDENCE"` | `ai_module/rules/rule_engine.py` |
| `DATA_QUALITY_ISSUE` | **Standard Data Quality Issues** | Format violations: inverted dates, negative values, out-of-bound coordinates, mismatched state-district linkages, missing IDs. | `is_anomaly=True`<br>`anomaly_type="DATA_QUALITY_ISSUE"` | `data/synthetic_generator/validator.py` |

---

## 2. In-Depth Scenario Specifications

### Scenario 1: Payment-Progress Mismatch (`PAYMENT_PROGRESS_MISMATCH`)
- **Mechanism**: In projects executing on milestone-based disbursement, funds should correspond to verified physical progress stages (e.g. Foundation, Structure, Finishing). In this scenario, funds are disbursed in advance or without commensurate physical milestone progress on site.
- **Example Data Pattern**:
  - `sanctioned_amount`: ₹20,00,000
  - `cumulative_payments`: ₹18,50,000 ($92.5\%$)
  - `physical_progress_pct`: $15.0\%$
  - `status`: `In Progress`
- **Neutral Audit Finding**: `"Severe financial-physical divergence: 92.5% of sanctioned funds disbursed while physical progress is recorded at 15.0%."`

---

### Scenario 2: Cost Outlier (`COST_OUTLIER`)
- **Mechanism**: In a given category (e.g. *Drinking Water* where median is ₹5,00,000), a work is sanctioned at ₹38,00,000 ($7.6\times$ the median) without proportionate increase in physical deliverables.
- **Detection Heuristic**: $Z$-score or Modified $Z$-score (MAD) $> 3.5$ relative to category peer group in the same geographic cluster.
- **Neutral Audit Finding**: `"Cost outlier: Sanctioned amount of Rs. 38,00,000 is 7.6x higher than standard category median benchmark of Rs. 5,00,000."`

---

### Scenario 3: Stalled Work (`STALLED_WORK`)
- **Mechanism**: A project was commenced over a year ago with a stipulated completion timeline of 180 days. Target completion date has passed by over 200 days, and no milestone progress updates or inspection records have been recorded for over 6 months.
- **Example Data Pattern**:
  - `commencement_date`: `2023-05-10`
  - `target_completion_date`: `2023-11-10`
  - `latest_update_date`: `2023-08-15`
  - `physical_progress_pct`: $32.0\%$
  - `status`: `Stalled`
- **Neutral Audit Finding**: `"Stalled project: Target completion date elapsed with progress stuck at 32.0% and no physical updates for over 200 days."`

---

### Scenario 4: Possible Duplicate Recommendation (`POSSIBLE_DUPLICATE`)
- **Mechanism**: Multiple work recommendations submitted within the same district or parliamentary constituency featuring near-identical titles (e.g. Levenshtein string distance $> 90\%$ or TF-IDF cosine similarity $> 0.85$), same category, and similar budget.
- **Example Pair**:
  - Work A (`MPLAD-WRK-000120`): *"Construction of Community Hall at Haveli Sector-4"* (Sanction: ₹20,00,000)
  - Work B (`MPLAD-WRK-000845`): *"Erection of Community Hall in Haveli Sector-4"* (Sanction: ₹20,00,000)
- **Neutral Audit Finding**: `"Potential duplicate recommendation: Highly similar scope and title matching work MPLAD-WRK-000120 in district Pune, category 'Community Infrastructure & Halls'."`

---

### Scenario 5: Missing Completion Evidence (`MISSING_COMPLETION_EVIDENCE`)
- **Mechanism**: Administrative status is toggled to `Completed` and cumulative payments show $100\%$ disbursement, but the formal closeout documentation is missing (no `actual_completion_date`, no final inspection record, and no physical asset registration).
- **Neutral Audit Finding**: `"Incomplete closure documentation: Work marked as 100% completed with full financial disbursement, but lacks mandatory actual completion date and final inspection sign-off."`

---

## 3. Evaluation & Risk Scoring Integration

For testing and grading automated risk engines:
1. **Precision / Recall on Demonstration Labels**: Evaluate detector precision and recall against `is_anomaly` and `anomaly_type`.
2. **Composite Risk Score Formula**:
   $$\text{RiskScore} = w_1 \cdot \text{PaymentMismatchScore} + w_2 \cdot \text{CostOutlierScore} + w_3 \cdot \text{DelayScore} + w_4 \cdot \text{ComplianceScore}$$
3. **Data Quality Gate**: Data quality errors (CRITICAL / ERROR) block upload ingestion before risk scoring executes.
