import { useCallback, useEffect, useMemo, useState } from "react";
import { RiskCase } from "../types";
import { fetchRiskCases, updateCaseStatus } from "../services/api";

interface UseRiskCasesResult {
  cases: RiskCase[];
  loading: boolean;
  error: string | null;
  refresh: () => void;
  setStatus: (caseId: string, status: RiskCase["status"]) => Promise<void>;
  counts: Record<RiskCase["risk_level"], number>;
}

export function useRiskCases(): UseRiskCasesResult {
  const [cases, setCases] = useState<RiskCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchRiskCases()
      .then(setCases)
      .catch(() => setError("Could not load risk cases. Try refreshing."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const setStatus = useCallback(async (caseId: string, status: RiskCase["status"]) => {
    await updateCaseStatus(caseId, status);
    setCases((prev) => prev.map((c) => (c.id === caseId ? { ...c, status } : c)));
  }, []);

  const counts = useMemo(() => {
    const base: Record<RiskCase["risk_level"], number> = { low: 0, medium: 0, high: 0, critical: 0 };
    cases.forEach((c) => {
      base[c.risk_level] += 1;
    });
    return base;
  }, [cases]);

  return { cases, loading, error, refresh: load, setStatus, counts };
}
