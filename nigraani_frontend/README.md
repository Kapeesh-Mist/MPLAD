# Nigraani — Public Works Oversight (Frontend)

React + TypeScript + Vite + Tailwind CSS frontend for the Nigraani platform:
flagging cost/timeline/documentation risk on public works, tracking field
inspections, and maintaining an audit trail.

## Getting started

```bash
npm install
cp .env.example .env
npm run dev
```

The app runs against built-in demo data out of the box (`VITE_USE_MOCK=true`),
so you can explore every screen — login, dashboard, risk queue, case detail,
field map, inspection plan, and audit trail — without the backend running.

To connect to the real FastAPI backend in `backend/app`:

1. Start the backend (`uvicorn app.main:app --reload`, default `:8000`).
2. In `.env`, set `VITE_USE_MOCK=false` and `VITE_API_BASE_URL` to the
   backend's `/api` root.
3. Restart `npm run dev`.

All backend calls are centralized in `src/services/api.ts` — each function
already maps to the corresponding FastAPI route (`auth.py`, `users.py`,
`works.py`, `risk_cases.py`, `audit.py`).

## Structure

```
src/
  components/   Sidebar, Topbar, Layout, RiskCard, EvidenceTable, AuditLog, Badge, StatCard, ProtectedRoute
  context/      AuthContext (JWT session state)
  hooks/        useAuth, useRiskCases
  pages/        Login, Dashboard, RiskQueue, CaseDetail, MapView, InspectionPlan, AuditTrail
  services/     api.ts (backend client), mockData.ts (demo dataset)
  utils/        format.ts (currency/date helpers)
  types.ts      Shared domain types mirroring backend models
```

## Design

Ink-navy (`#0F1B2D`) and paper (`#F6F4EE`) base with an ochre accent
(`#C17817`) for flagged/high-priority states, rust for critical risk, and
moss green for resolved/verified. Source Serif 4 for headings, Inter for
body and data, IBM Plex Mono for case IDs and timestamps — meant to read as
an official oversight ledger rather than a generic SaaS dashboard.

## Login (demo mode)

Any password signs you in as the seeded auditor account. Swap in real
authentication once `VITE_USE_MOCK=false`.
