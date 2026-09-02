import React from "react";

type AuditEntry = {
  id: string | number;
  actor: string;
  action: string;
  entity_ref: string;
  timestamp: string;
  detail: string;
  actor_role: string;
  ip_address?: string;
};

const ACTION_COLOR: Record<string, string> = {
  escalated_case: "bg-red-500",
  case_flagged: "bg-yellow-500",
  submitted_evidence: "bg-blue-500",
  risk_score_recalculated: "bg-gray-500",
  assigned_case: "bg-blue-500",
  resolved_case: "bg-green-500",
  scheduled_inspection: "bg-gray-500",
};

function formatDateTime(timestamp: string): string {
  const date = new Date(timestamp);

  if (isNaN(date.getTime())) {
    return timestamp;
  }

  return date.toLocaleString();
}

function humanizeAction(action: string): string {
  return action.replace(/_/g, " ");
}

export default function AuditLog({
  entries,
}: {
  entries: AuditEntry[];
}) {
  if (!entries || entries.length === 0) {
    return (
      <div className="p-8 text-center">
        <p className="text-sm text-slate-500">
          No activity has been recorded yet.
        </p>
      </div>
    );
  }

  return (
    <ol className="relative">
      {entries.map((entry, idx) => (
        <li
          key={entry.id}
          className="relative flex gap-4 pb-7 last:pb-0"
        >
          {/* Timeline line */}
          {idx !== entries.length - 1 && (
            <span className="absolute left-[5px] top-3 bottom-0 w-px bg-slate-200" />
          )}

          {/* Timeline dot */}
          <span
            className={`mt-1.5 h-[11px] w-[11px] shrink-0 rounded-full ring-4 ring-white ${
              ACTION_COLOR[entry.action] || "bg-gray-500"
            }`}
          />

          {/* Activity card */}
          <div className="min-w-0 flex-1 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            {/* Header */}
            <div className="mb-1.5 flex items-start justify-between gap-3">
              <p className="text-sm text-slate-900">
                <span className="font-medium">
                  {entry.actor}
                </span>{" "}

                <span className="text-slate-500">
                  {humanizeAction(entry.action)}
                </span>{" "}

                <span className="font-mono text-xs text-slate-600">
                  {entry.entity_ref}
                </span>
              </p>

              <p className="whitespace-nowrap text-xs text-slate-500">
                {formatDateTime(entry.timestamp)}
              </p>
            </div>

            {/* Details */}
            <p className="text-sm leading-relaxed text-slate-600">
              {entry.detail}
            </p>

            {/* User information */}
            <div className="mt-2 flex items-center gap-3">
              <span className="text-[11px] uppercase tracking-wide text-slate-400">
                {entry.actor_role}
              </span>

              {entry.ip_address && (
                <span className="font-mono text-xs text-slate-500">
                  {entry.ip_address}
                </span>
              )}
            </div>
          </div>
        </li>
      ))}
    </ol>
  );
}