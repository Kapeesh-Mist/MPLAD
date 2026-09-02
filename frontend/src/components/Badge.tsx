import React from "react";
import { CaseStatus, RiskLevel } from "../types";

const RISK_STYLES: Record<RiskLevel, string> = {
  critical: "bg-rust-500 text-paper-100",
  high: "bg-ochre-500 text-paper-100",
  medium: "bg-ochre-100 text-ochre-600",
  low: "bg-moss-50 text-moss-500",
};

const RISK_LABEL: Record<RiskLevel, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
};

export function RiskBadge({ level }: { level: RiskLevel }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-sm text-xs font-medium ${RISK_STYLES[level]}`}>
      {RISK_LABEL[level]}
    </span>
  );
}

const STATUS_STYLES: Record<CaseStatus, string> = {
  open: "border-ochre-400 text-ochre-600",
  under_review: "border-ink-600 text-ink-700",
  escalated: "border-rust-500 text-rust-500",
  resolved: "border-moss-400 text-moss-500",
  dismissed: "border-slate-300 text-slate-500",
};

const STATUS_LABEL: Record<CaseStatus, string> = {
  open: "Open",
  under_review: "Under review",
  escalated: "Escalated",
  resolved: "Resolved",
  dismissed: "Dismissed",
};

export function StatusBadge({ status }: { status: CaseStatus }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-sm text-xs font-medium border ${STATUS_STYLES[status]}`}>
      {STATUS_LABEL[status]}
    </span>
  );
}
