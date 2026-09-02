import React from "react";
import { Evidence } from "../types";
import { formatDate } from "../utils/format";

const TYPE_LABEL: Record<Evidence["type"], string> = {
  document: "Document",
  photo: "Photograph",
  geotag: "Geotag",
  financial: "Financial record",
  statement: "Statement",
};

export default function EvidenceTable({ evidence }: { evidence: Evidence[] }) {
  if (evidence.length === 0) {
    return (
      <div className="panel p-8 text-center">
        <p className="text-sm text-slate-500">No evidence has been logged against this case yet.</p>
      </div>
    );
  }

  return (
    <div className="panel overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-paper-200/50">
            <th className="text-left font-medium text-slate-500 text-xs px-5 py-3">Reference</th>
            <th className="text-left font-medium text-slate-500 text-xs px-5 py-3">Item</th>
            <th className="text-left font-medium text-slate-500 text-xs px-5 py-3">Type</th>
            <th className="text-left font-medium text-slate-500 text-xs px-5 py-3">Submitted by</th>
            <th className="text-left font-medium text-slate-500 text-xs px-5 py-3">Date</th>
            <th className="text-left font-medium text-slate-500 text-xs px-5 py-3">Status</th>
          </tr>
        </thead>
        <tbody>
          {evidence.map((item, idx) => (
            <tr
              key={item.id}
              className={idx !== evidence.length - 1 ? "border-b border-slate-100" : ""}
            >
              <td className="px-5 py-3.5 case-id whitespace-nowrap">{item.reference}</td>
              <td className="px-5 py-3.5 text-ink-900">{item.title}</td>
              <td className="px-5 py-3.5 text-slate-600">{TYPE_LABEL[item.type]}</td>
              <td className="px-5 py-3.5 text-slate-600">{item.submitted_by}</td>
              <td className="px-5 py-3.5 text-slate-600 whitespace-nowrap">{formatDate(item.submitted_at)}</td>
              <td className="px-5 py-3.5">
                {item.verified ? (
                  <span className="inline-flex items-center gap-1.5 text-moss-500 text-xs font-medium">
                    <span className="w-1.5 h-1.5 rounded-full bg-moss-400" /> Verified
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 text-ochre-600 text-xs font-medium">
                    <span className="w-1.5 h-1.5 rounded-full bg-ochre-400" /> Pending
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
