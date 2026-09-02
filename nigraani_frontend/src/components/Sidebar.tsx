import React from "react";
import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Overview", end: true },
  { to: "/risk-queue", label: "Risk queue" },
  { to: "/map", label: "Field map" },
  { to: "/inspections", label: "Inspection plan" },
  { to: "/audit-trail", label: "Audit trail" },
];

export default function Sidebar() {
  return (
    <aside className="hidden lg:flex flex-col w-60 shrink-0 bg-ink-900 text-paper-100 h-screen sticky top-0">
      <div className="px-6 py-6 border-b border-ink-700">
        <div className="flex items-center gap-2.5">
          <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 2L23 6.5V13C23 19 18.5 23.2 13 24.5C7.5 23.2 3 19 3 13V6.5L13 2Z" stroke="#D69A32" strokeWidth="1.6" strokeLinejoin="round" />
            <path d="M8.5 13.2L11.3 16L18 9" stroke="#D69A32" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <div>
            <p className="font-serif text-lg leading-none">Nigraani</p>
            <p className="text-[11px] text-slate-300 mt-0.5">Public Works Oversight</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-5 space-y-0.5">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3 py-2.5 rounded text-sm transition-colors ${
                isActive
                  ? "bg-ink-700 text-paper-100 font-medium"
                  : "text-slate-300 hover:bg-ink-800 hover:text-paper-100"
              }`
            }
          >
            <NavDot to={item.to} />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="px-6 py-5 border-t border-ink-700">
        <p className="text-[11px] text-slate-300 leading-relaxed">
          Data reflects the most recent sync from field agencies.
        </p>
      </div>
    </aside>
  );
}

function NavDot({ to }: { to: string }) {
 const icons: Record<string, React.ReactElement> = {
    "/": <circle cx="4" cy="4" r="3.5" />,
    "/risk-queue": <rect x="0.5" y="0.5" width="7" height="7" rx="1.5" />,
    "/map": <path d="M4 0.5L7.5 4L4 7.5L0.5 4Z" />,
    "/inspections": <path d="M0.5 2H7.5M0.5 4H7.5M0.5 6H5" strokeLinecap="round" />,
    "/audit-trail": <path d="M4 0.5V7.5M0.5 4H7.5" strokeLinecap="round" />,
  };
  return (
    <svg width="8" height="8" viewBox="0 0 8 8" fill="none" stroke="currentColor" strokeWidth="1.2" className="opacity-70 shrink-0">
      {icons[to]}
    </svg>
  );
}
