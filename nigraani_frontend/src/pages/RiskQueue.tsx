import React, { useMemo, useState } from "react";
import Layout from "../components/Layout";
import RiskCard from "../components/RiskCard";
import { useRiskCases } from "../hooks/useRiskCases";
import { CaseStatus, RiskLevel } from "../types";

const RISK_FILTERS: (RiskLevel | "all")[] = ["all", "critical", "high", "medium", "low"];
const STATUS_FILTERS: (CaseStatus | "all")[] = ["all", "open", "under_review", "escalated", "resolved", "dismissed"];

export default function RiskQueue() {
  const { cases, loading, error } = useRiskCases();
  const [riskFilter, setRiskFilter] = useState<RiskLevel | "all">("all");
  const [statusFilter, setStatusFilter] = useState<CaseStatus | "all">("all");
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    return cases
      .filter((c) => riskFilter === "all" || c.risk_level === riskFilter)
      .filter((c) => statusFilter === "all" || c.status === statusFilter)
      .filter((c) =>
        query.trim() === ""
          ? true
          : `${c.work_title} ${c.case_number} ${c.agency_name}`.toLowerCase().includes(query.toLowerCase())
      )
      .sort((a, b) => b.risk_score - a.risk_score);
  }, [cases, riskFilter, statusFilter, query]);

  return (
    <Layout title="Risk queue" subtitle={`${filtered.length} of ${cases.length} cases shown`}>
      <div className="flex flex-col md:flex-row gap-4 md:items-center justify-between mb-6">
        <input
          type="text"
          placeholder="Search by case, work, or agency…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="field-input max-w-sm"
        />

        <div className="flex flex-wrap gap-2">
          <FilterGroup
            options={RISK_FILTERS}
            active={riskFilter}
            onChange={setRiskFilter}
            labelFor={(v) => (v === "all" ? "All risk" : v[0].toUpperCase() + v.slice(1))}
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-8">
        <FilterGroup
          options={STATUS_FILTERS}
          active={statusFilter}
          onChange={setStatusFilter}
          labelFor={(v) => (v === "all" ? "All statuses" : v.replace("_", " "))}
          variant="pill"
        />
      </div>

      {loading && <div className="panel p-10 text-center text-sm text-slate-500">Loading risk cases…</div>}
      {error && <div className="panel p-10 text-center text-sm text-rust-500">{error}</div>}

      {!loading && !error && filtered.length === 0 && (
        <div className="panel p-10 text-center">
          <p className="text-sm text-slate-500">No cases match these filters.</p>
        </div>
      )}

      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filtered.map((c) => (
          <RiskCard key={c.id} riskCase={c} />
        ))}
      </div>
    </Layout>
  );
}

function FilterGroup<T extends string>({
  options,
  active,
  onChange,
  labelFor,
  variant = "tab",
}: {
  options: T[];
  active: T;
  onChange: (v: T) => void;
  labelFor: (v: T) => string;
  variant?: "tab" | "pill";
}) {
  return (
    <div className={variant === "tab" ? "flex bg-paper-200 rounded p-1" : "flex flex-wrap gap-2"}>
      {options.map((opt) => {
        const isActive = opt === active;
        if (variant === "pill") {
          return (
            <button
              key={opt}
              onClick={() => onChange(opt)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium border capitalize transition-colors ${
                isActive
                  ? "bg-ink-900 text-paper-100 border-ink-900"
                  : "bg-transparent text-slate-600 border-slate-200 hover:border-ink-700"
              }`}
            >
              {labelFor(opt)}
            </button>
          );
        }
        return (
          <button
            key={opt}
            onClick={() => onChange(opt)}
            className={`px-3 py-1.5 rounded text-xs font-medium capitalize transition-colors ${
              isActive ? "bg-paper-100 text-ink-900 shadow-card" : "text-slate-500 hover:text-ink-900"
            }`}
          >
            {labelFor(opt)}
          </button>
        );
      })}
    </div>
  );
}
