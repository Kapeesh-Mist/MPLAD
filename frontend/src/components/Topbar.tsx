import React, { useState } from "react";
import { useAuth } from "../hooks/useAuth";

export default function Topbar({ title, subtitle }: { title: string; subtitle?: string }) {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  const initials = user?.full_name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <header className="flex items-center justify-between px-6 lg:px-10 py-5 border-b border-slate-100 bg-paper-100/80 backdrop-blur sticky top-0 z-10">
      <div>
        <h1 className="font-serif text-2xl text-ink-900">{title}</h1>
        {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
      </div>

      <div className="relative flex items-center gap-4">
        <div className="hidden md:block text-right">
          <p className="text-sm font-medium text-ink-900">{user?.full_name}</p>
          <p className="text-xs text-slate-500">{user?.agency_name}</p>
        </div>
        <button
          onClick={() => setMenuOpen((o) => !o)}
          className="w-9 h-9 rounded-full bg-ink-900 text-paper-100 text-xs font-semibold flex items-center justify-center hover:bg-ink-800 transition-colors"
        >
          {initials || "NG"}
        </button>
        {menuOpen && (
          <div className="absolute right-0 top-12 w-44 panel py-1.5 z-20">
            <button
              onClick={logout}
              className="w-full text-left px-4 py-2 text-sm text-rust-500 hover:bg-rust-50 transition-colors"
            >
              Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
