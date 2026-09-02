import React, { useEffect, useMemo, useState } from "react";
import Layout from "../components/Layout";
import AuditLog from "../components/AuditLog";
import { fetchAuditTrail } from "../services/api";
import { AuditEntry } from "../types";

export default function AuditTrail() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");

  useEffect(() => {
    fetchAuditTrail()
      .then(setEntries)
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    if (!query.trim()) return entries;
    const q = query.toLowerCase();
    return entries.filter((e) =>
      `${e.actor} ${e.action} ${e.entity_ref} ${e.detail}`.toLowerCase().includes(q)
    );
  }, [entries, query]);

  return (
    <Layout title="Audit trail" subtitle="Immutable record of every action taken on the platform">
      <div className="flex items-center justify-between mb-6">
        <input
          type="text"
          placeholder="Search by actor, action, or case reference…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="field-input max-w-sm"
        />
        <p className="text-sm text-slate-500 hidden md:block">{filtered.length} entries</p>
      </div>

      {loading ? (
        <div className="panel p-10 text-center text-sm text-slate-500">Loading audit trail…</div>
      ) : (
        <AuditLog entries={filtered} />
      )}
    </Layout>
  );
}
