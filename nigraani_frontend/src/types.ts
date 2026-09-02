// Core domain types — mirror backend/app/models and schemas

export type UserRole = "admin" | "auditor" | "inspector" | "viewer";

export interface User {
  id: string;
  full_name: string;
  email: string;
  role: UserRole;
  agency_id?: string;
  agency_name?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
}

export type RiskLevel = "low" | "medium" | "high" | "critical";
export type CaseStatus = "open" | "under_review" | "escalated" | "resolved" | "dismissed";

export interface Location {
  id: string;
  district: string;
  state: string;
  latitude: number;
  longitude: number;
}

export interface Agency {
  id: string;
  name: string;
  code: string;
  jurisdiction: string;
}

export interface Work {
  id: string;
  title: string;
  work_code: string;
  agency_id: string;
  agency_name: string;
  location: Location;
  sanctioned_amount: number;
  spent_amount: number;
  start_date: string;
  expected_completion: string;
  status: "planned" | "in_progress" | "delayed" | "completed" | "stalled";
  progress_pct: number;
}

export interface RiskSignal {
  id: string;
  label: string;
  detail: string;
  weight: number;
}

export interface RiskCase {
  id: string;
  case_number: string;
  work_id: string;
  work_title: string;
  work_code: string;
  agency_name: string;
  location: Location;
  risk_level: RiskLevel;
  risk_score: number;
  status: CaseStatus;
  signals: RiskSignal[];
  flagged_at: string;
  assigned_to?: string;
  sanctioned_amount: number;
  spent_amount: number;
  summary: string;
}

export interface Evidence {
  id: string;
  case_id: string;
  type: "document" | "photo" | "geotag" | "financial" | "statement";
  title: string;
  submitted_by: string;
  submitted_at: string;
  reference: string;
  verified: boolean;
}

export interface AuditEntry {
  id: string;
  actor: string;
  actor_role: UserRole;
  action: string;
  entity_type: string;
  entity_ref: string;
  timestamp: string;
  detail: string;
  ip_address?: string;
}

export interface InspectionTask {
  id: string;
  case_id: string;
  case_number: string;
  work_title: string;
  location: Location;
  scheduled_date: string;
  assigned_to: string;
  priority: RiskLevel;
  status: "pending" | "scheduled" | "in_progress" | "completed";
  checklist: { id: string; label: string; done: boolean }[];
}

export interface DashboardStats {
  total_works: number;
  active_works: number;
  open_cases: number;
  critical_cases: number;
  total_sanctioned: number;
  total_spent: number;
  flagged_amount: number;
  resolution_rate: number;
}
