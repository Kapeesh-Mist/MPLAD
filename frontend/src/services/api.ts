import axios, { AxiosError } from "axios";
import {
  AuditEntry,
  DashboardStats,
  Evidence,
  InspectionTask,
  RiskCase,
  User,
  Work,
} from "../types";
import {
  mockAuditTrail,
  mockEvidence,
  mockInspections,
  mockRiskCases,
  mockStats,
  mockUser,
  mockWorks,
} from "./mockData";

// Set VITE_USE_MOCK=false once the FastAPI backend (backend/app) is reachable
// at VITE_API_BASE_URL. Defaults to demo data so the UI is usable standalone.
const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? "true") !== "false";
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

export const client = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("nigraani_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("nigraani_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

const delay = <T>(value: T, ms = 380): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(value), ms));

// ---------------------------------------------------------------------------
// Auth — maps to backend/app/api/routes/auth.py
// ---------------------------------------------------------------------------
export async function login(email: string, password: string): Promise<{ user: User; token: string }> {
  if (USE_MOCK) {
    if (!email || !password) throw new Error("Email and password are required");
    return delay({ user: mockUser, token: "demo-token-" + Date.now() }, 550);
  }
  const { data } = await client.post("/auth/login", { email, password });
  return data;
}

export async function fetchCurrentUser(): Promise<User> {
  if (USE_MOCK) return delay(mockUser);
  const { data } = await client.get("/users/me");
  return data;
}

// ---------------------------------------------------------------------------
// Dashboard / Works — maps to routes/works.py
// ---------------------------------------------------------------------------
export async function fetchDashboardStats(): Promise<DashboardStats> {
  if (USE_MOCK) return delay(mockStats);
  const { data } = await client.get("/works/stats");
  return data;
}

export async function fetchWorks(): Promise<Work[]> {
  if (USE_MOCK) return delay(mockWorks);
  const { data } = await client.get("/works");
  return data;
}

// ---------------------------------------------------------------------------
// Risk cases — maps to routes/risk_cases.py
// ---------------------------------------------------------------------------
export async function fetchRiskCases(): Promise<RiskCase[]> {
  if (USE_MOCK) return delay(mockRiskCases);
  const { data } = await client.get("/risk-cases");
  return data;
}

export async function fetchRiskCase(id: string): Promise<RiskCase | undefined> {
  if (USE_MOCK) return delay(mockRiskCases.find((c) => c.id === id));
  const { data } = await client.get(`/risk-cases/${id}`);
  return data;
}

export async function fetchEvidenceForCase(caseId: string): Promise<Evidence[]> {
  if (USE_MOCK) return delay(mockEvidence.filter((e) => e.case_id === caseId));
  const { data } = await client.get(`/risk-cases/${caseId}/evidence`);
  return data;
}

export async function updateCaseStatus(caseId: string, status: RiskCase["status"]): Promise<void> {
  if (USE_MOCK) {
    const target = mockRiskCases.find((c) => c.id === caseId);
    if (target) target.status = status;
    return delay(undefined, 250);
  }
  await client.patch(`/risk-cases/${caseId}`, { status });
}

// ---------------------------------------------------------------------------
// Audit — maps to routes/audit.py
// ---------------------------------------------------------------------------
export async function fetchAuditTrail(): Promise<AuditEntry[]> {
  if (USE_MOCK) return delay(mockAuditTrail);
  const { data } = await client.get("/audit");
  return data;
}

// ---------------------------------------------------------------------------
// Inspections (works + risk_case_service composite) — routes/works.py
// ---------------------------------------------------------------------------
export async function fetchInspections(): Promise<InspectionTask[]> {
  if (USE_MOCK) return delay(mockInspections);
  const { data } = await client.get("/works/inspections");
  return data;
}
