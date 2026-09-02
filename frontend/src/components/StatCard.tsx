import React from "react";

interface StatCardProps {
  label: string;
  value: string;
  detail?: string;
  tone?: "default" | "alert";
}

export default function StatCard({ label, value, detail, tone = "default" }: StatCardProps) {
  return (
    <div className="panel p-5">
      <p className="text-[11px] text-slate-500">{label}</p>
      <p className={`font-serif text-3xl mt-1.5 ${tone === "alert" ? "text-rust-500" : "text-ink-900"}`}>
        {value}
      </p>
      {detail && <p className="text-xs text-slate-500 mt-1.5">{detail}</p>}
    </div>
  );
}
