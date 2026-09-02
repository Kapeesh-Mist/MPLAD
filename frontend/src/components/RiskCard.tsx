import React from "react";
import { Link } from "react-router-dom";
import { RiskCase } from "../types";
import { RiskBadge, StatusBadge } from "./Badge";
import { formatINR, timeAgo } from "../utils/format";

const RISK_BAR: Record<RiskCase["risk_level"], string> = {
  critical: "bg-rust-500",
  high: "bg-ochre-500",
  medium: "bg-ochre-400",
  low: "bg-moss-400",
};

export default function RiskCard({ riskCase }: { riskCase: RiskCase }) {
  const utilisation = Math.round((riskCase.spent_amount / riskCase.sanctioned_amount) * 100);

  return (
    <Link
      to={`/risk-queue/${riskCase.id}`}
      className="block panel hover:shadow-panel hover:border-slate-300 transition-all group"
    >
      <div className={`h-1 rounded-t ${RISK_BAR[riskCase.risk_level]}`} />
      <div className="p-5">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="min-w-0">
            <p className="case-id">{riskCase.case_number}</p>
            <h3 className="font-serif text-lg text-ink-900 leading-snug mt-0.5 group-hover:underline decoration-1 underline-offset-2">
              {riskCase.work_title}
            </h3>
          </div>
          <RiskBadge level={riskCase.risk_level} />
        </div>

        <p className="text-sm text-slate-600 leading-relaxed line-clamp-2 mb-4">{riskCase.summary}</p>

        <div className="grid grid-cols-3 gap-4 mb-4 pb-4 divider">
          <div>
            <p className="text-[11px] text-slate-500">Risk score</p>
            <p className="text-sm font-medium text-ink-900 mt-0.5">{riskCase.risk_score}/100</p>
          </div>
          <div>
            <p className="text-[11px] text-slate-500">Utilisation</p>
            <p className="text-sm font-medium text-ink-900 mt-0.5">{utilisation}%</p>
          </div>
          <div>
            <p className="text-[11px] text-slate-500">Sanctioned</p>
            <p className="text-sm font-medium text-ink-900 mt-0.5">{formatINR(riskCase.sanctioned_amount)}</p>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <StatusBadge status={riskCase.status} />
          <p className="text-xs text-slate-500">
            {riskCase.agency_name} · flagged {timeAgo(riskCase.flagged_at)}
          </p>
        </div>
      </div>
    </Link>
  );
}
