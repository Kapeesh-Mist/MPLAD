import React, { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const { user, login, error } = useAuth();
  const [email, setEmail] = useState("ananya.krishnan@nigraani.gov.in");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await login(email, password);
    } catch {
      // error surfaced via context
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-paper">
      {/* Left — identity panel */}
      <div className="hidden lg:flex flex-col justify-between bg-ink-900 text-paper-100 p-14">
        <div className="flex items-center gap-2.5">
          <svg width="30" height="30" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 2L23 6.5V13C23 19 18.5 23.2 13 24.5C7.5 23.2 3 19 3 13V6.5L13 2Z" stroke="#D69A32" strokeWidth="1.6" strokeLinejoin="round" />
            <path d="M8.5 13.2L11.3 16L18 9" stroke="#D69A32" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span className="font-serif text-xl">Nigraani</span>
        </div>

        <div className="max-w-md">
          <p className="label-eyebrow text-ochre-100 mb-4">Public works oversight</p>
          <h1 className="font-serif text-4xl leading-tight mb-5">
            Every rupee sanctioned, traced to work completed.
          </h1>
          <p className="text-slate-300 text-base leading-relaxed">
            Nigraani flags cost, timeline, and documentation anomalies across public works in real
            time, and keeps an unbroken audit trail from field inspection to case resolution.
          </p>
        </div>

        <div className="flex gap-10 text-sm">
          <div>
            <p className="font-serif text-2xl">214</p>
            <p className="text-slate-300 mt-0.5">Works tracked</p>
          </div>
          <div>
            <p className="font-serif text-2xl">37</p>
            <p className="text-slate-300 mt-0.5">Open cases</p>
          </div>
          <div>
            <p className="font-serif text-2xl">72%</p>
            <p className="text-slate-300 mt-0.5">Resolution rate</p>
          </div>
        </div>
      </div>

      {/* Right — form */}
      <div className="flex items-center justify-center p-8">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-2.5 mb-10">
            <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 2L23 6.5V13C23 19 18.5 23.2 13 24.5C7.5 23.2 3 19 3 13V6.5L13 2Z" stroke="#C17817" strokeWidth="1.6" strokeLinejoin="round" />
              <path d="M8.5 13.2L11.3 16L18 9" stroke="#C17817" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span className="font-serif text-xl text-ink-900">Nigraani</span>
          </div>

          <h2 className="font-serif text-2xl text-ink-900 mb-1.5">Sign in to your workspace</h2>
          <p className="text-sm text-slate-500 mb-8">
            Use the credentials issued by your agency administrator.
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="field-label" htmlFor="email">
                Official email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="field-input"
                placeholder="name@agency.gov.in"
              />
            </div>

            <div>
              <label className="field-label" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="field-input"
                placeholder="Enter your password"
              />
            </div>

            {error && (
              <p className="text-sm text-rust-500 bg-rust-50 border border-rust-500/20 rounded px-3.5 py-2.5">
                {error}
              </p>
            )}

            <button type="submit" disabled={submitting} className="btn-primary w-full mt-2">
              {submitting ? "Signing in…" : "Sign in"}
            </button>

            <p className="text-xs text-slate-500 text-center pt-2">
              Demo mode — any password signs you in as the auditor account shown above.
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
