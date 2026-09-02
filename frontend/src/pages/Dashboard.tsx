import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import StatCard from "../components/StatCard";
import RiskCard from "../components/RiskCard";
import { useAuth } from "../hooks/useAuth";
import { useRiskCases } from "../hooks/useRiskCases";
import { fetchDashboardStats, fetchWorks } from "../services/api";
import { DashboardStats, Work } from "../types";
import { formatINR } from "../utils/format";

export default function Dashboard() {
  const { user } = useAuth();
  const { cases, loading: casesLoading, counts } = useRiskCases();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [works, setWorks] = useState<Work[]>([]);

  useEffect(() => {
    fetchDashboardStats().then(setStats);
    fetchWorks().then(setWorks);
  }, []);

  const topCases = [...cases]
    .filter((c) => c.status !== "resolved" && c.status !== "dismissed")
    .sort((a, b) => b.risk_score - a.risk_score)
    .slice(0, 3);

  const flaggedWorks = works.filter((w) => w.status === "delayed" || w.status === "stalled");

  return (
    <Layout title="Overview" subtitle={`Welcome back, ${user?.full_name.split(" ")[0] ?? ""}`}>
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <StatCard
          label="Works tracked"
          value={stats ? stats.total_works.toString() : "—"}
          detail={stats ? `${stats.active_works} active` : undefined}
        />
        <StatCard
          label="Open risk cases"
          value={stats ? stats.open_cases.toString() : "—"}
          detail={stats ? `${stats.critical_cases} critical` : undefined}
          tone="alert"
        />
        <StatCard
          label="Funds sanctioned"
          value={stats ? formatINR(stats.total_sanctioned) : "—"}
          detail={stats ? `${formatINR(stats.total_spent)} utilised` : undefined}
        />
        <StatCard
          label="Amount under flag"
          value={stats ? formatINR(stats.flagged_amount) : "—"}
          detail={stats ? `${Math.round(stats.resolution_rate * 100)}% resolution rate` : undefined}
          tone="alert"
        />
      </section>

      <div className="grid lg:grid-cols-3 gap-8">
        <section className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-serif text-xl text-ink-900">Highest-priority cases</h2>
            <Link to="/risk-queue" className="text-sm text-ink-700 hover:text-ink-900 underline decoration-1 underline-offset-4">
              View full queue
            </Link>
          </div>

          {casesLoading ? (
            <div className="panel p-8 text-center text-sm text-slate-500">Loading risk cases…</div>
          ) : (
            <div className="space-y-4">
              {topCases.map((c) => (
                <RiskCard key={c.id} riskCase={c} />
              ))}
            </div>
          )}
        </section>

        <section>
          <h2 className="font-serif text-xl text-ink-900 mb-4">Risk distribution</h2>
          <div className="panel p-5 mb-6">
            {(["critical", "high", "medium", "low"] as const).map((level) => (
              <div key={level} className="flex items-center gap-3 py-2.5 first:pt-0 last:pb-0 border-b last:border-0 border-slate-100">
                <span
                  className={`w-2.5 h-2.5 rounded-full ${
                    level === "critical"
                      ? "bg-rust-500"
                      : level === "high"
                      ? "bg-ochre-500"
                      : level === "medium"
                      ? "bg-ochre-400"
                      : "bg-moss-400"
                  }`}
                />
                <span className="text-sm text-slate-600 capitalize flex-1">{level}</span>
                <span className="text-sm font-medium text-ink-900">{counts[level]}</span>
              </div>
            ))}
          </div>

          <h2 className="font-serif text-xl text-ink-900 mb-4">Works needing attention</h2>
          <div className="panel divide-y divide-slate-100">
            {flaggedWorks.map((w) => (
              <div key={w.id} className="p-4">
                <p className="text-sm font-medium text-ink-900 leading-snug">{w.title}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="case-id">{w.work_code}</span>
                  <span className="text-xs text-slate-500 capitalize">{w.status.replace("_", " ")}</span>
                </div>
                <div className="mt-2.5 h-1.5 bg-paper-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-ochre-500 rounded-full"
                    style={{ width: `${w.progress_pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </Layout>
  );
}
