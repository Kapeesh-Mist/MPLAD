import React, { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import Layout from "../components/Layout";
import EvidenceTable from "../components/EvidenceTable";
import { RiskBadge, StatusBadge } from "../components/Badge";
import { fetchEvidenceForCase, fetchRiskCase } from "../services/api";
import { useRiskCases } from "../hooks/useRiskCases";
import { CaseStatus, Evidence, RiskCase } from "../types";
import { formatDate, formatDateTime, formatINR } from "../utils/format";

const STATUS_OPTIONS: CaseStatus[] = ["open", "under_review", "escalated", "resolved", "dismissed"];

export default function CaseDetail() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const { setStatus } = useRiskCases();
  const [riskCase, setRiskCase] = useState<RiskCase | null | undefined>(undefined);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (!caseId) return;
    fetchRiskCase(caseId).then((c) => setRiskCase(c ?? null));
    fetchEvidenceForCase(caseId).then(setEvidence);
  }, [caseId]);

  if (riskCase === undefined) {
    return (
      <Layout title="Case detail">
        <div className="panel p-10 text-center text-sm text-slate-500">Loading case…</div>
      </Layout>
    );
  }

  if (riskCase === null) {
    return (
      <Layout title="Case not found">
        <div className="panel p-10 text-center">
          <p className="text-sm text-slate-500 mb-4">This case reference does not exist or has been removed.</p>
          <Link to="/risk-queue" className="btn-secondary">
            Back to risk queue
          </Link>
        </div>
      </Layout>
    );
  }

  async function handleStatusChange(next: CaseStatus) {
    if (!riskCase) return;
    setUpdating(true);
    await setStatus(riskCase.id, next);
    setRiskCase({ ...riskCase, status: next });
    setUpdating(false);
  }

  const utilisation = Math.round((riskCase.spent_amount / riskCase.sanctioned_amount) * 100);

  return (
    <Layout title={riskCase.case_number} subtitle={riskCase.work_title}>
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-slate-500 hover:text-ink-900 mb-6 inline-flex items-center gap-1.5"
      >
        ← Back
      </button>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <section className="panel p-6">
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <RiskBadge level={riskCase.risk_level} />
                  <StatusBadge status={riskCase.status} />
                </div>
                <h2 className="font-serif text-2xl text-ink-900 leading-snug">{riskCase.work_title}</h2>
                <p className="case-id mt-1">{riskCase.work_code} · {riskCase.agency_name}</p>
              </div>
              <div className="text-right shrink-0">
                <p className="text-[11px] text-slate-500">Risk score</p>
                <p className="font-serif text-3xl text-ink-900">{riskCase.risk_score}</p>
              </div>
            </div>
            <p className="text-sm text-slate-600 leading-relaxed divider pt-4">{riskCase.summary}</p>
          </section>

          <section>
            <h3 className="font-serif text-lg text-ink-900 mb-3">Risk signals</h3>
            <div className="space-y-3">
              {riskCase.signals.map((signal) => (
                <div key={signal.id} className="panel p-4 flex items-start gap-4">
                  <div className="w-11 h-11 rounded-full bg-paper-200 flex items-center justify-center shrink-0">
                    <span className="text-xs font-medium text-ink-900">{signal.weight}</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-ink-900">{signal.label}</p>
                    <p className="text-sm text-slate-600 mt-0.5">{signal.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h3 className="font-serif text-lg text-ink-900 mb-3">Evidence log</h3>
            <EvidenceTable evidence={evidence} />
          </section>
        </div>

        <aside className="space-y-6">
          <div className="panel p-5">
            <p className="text-[11px] text-slate-500 mb-3">Case status</p>
            <select
              value={riskCase.status}
              disabled={updating}
              onChange={(e) => handleStatusChange(e.target.value as CaseStatus)}
              className="field-input capitalize"
            >
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s} className="capitalize">
                  {s.replace("_", " ")}
                </option>
              ))}
            </select>
            {riskCase.assigned_to && (
              <p className="text-xs text-slate-500 mt-3">Assigned to {riskCase.assigned_to}</p>
            )}
            <p className="text-xs text-slate-500 mt-1">Flagged {formatDateTime(riskCase.flagged_at)}</p>
          </div>

          <div className="panel p-5">
            <p className="text-[11px] text-slate-500 mb-3">Financials</p>
            <dl className="space-y-3">
              <Row label="Sanctioned amount" value={formatINR(riskCase.sanctioned_amount)} />
              <Row label="Spent to date" value={formatINR(riskCase.spent_amount)} />
              <Row label="Utilisation" value={`${utilisation}%`} />
            </dl>
            <div className="mt-3 h-1.5 bg-paper-200 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${utilisation > 90 ? "bg-rust-500" : "bg-ochre-500"}`}
                style={{ width: `${Math.min(utilisation, 100)}%` }}
              />
            </div>
          </div>

          <div className="panel p-5">
            <p className="text-[11px] text-slate-500 mb-3">Location</p>
            <p className="text-sm text-ink-900">{riskCase.location.district}, {riskCase.location.state}</p>
            <Link
              to="/map"
              className="text-xs text-ink-700 hover:text-ink-900 underline decoration-1 underline-offset-4 mt-2 inline-block"
            >
              View on field map
            </Link>
          </div>
        </aside>
      </div>
    </Layout>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <dt className="text-sm text-slate-500">{label}</dt>
      <dd className="text-sm font-medium text-ink-900">{value}</dd>
    </div>
  );
}
