import React, { useEffect, useState } from "react";
import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import { RiskBadge } from "../components/Badge";
import { fetchRiskCases } from "../services/api";
import { RiskCase } from "../types";
import { formatINR } from "../utils/format";

const RISK_COLOR: Record<RiskCase["risk_level"], string> = {
  critical: "#B3311D",
  high: "#C17817",
  medium: "#D69A32",
  low: "#2F6844",
};

const RISK_RADIUS: Record<RiskCase["risk_level"], number> = {
  critical: 12,
  high: 10,
  medium: 8,
  low: 7,
};

export default function MapView() {
  const [cases, setCases] = useState<RiskCase[]>([]);

  useEffect(() => {
    fetchRiskCases().then(setCases);
  }, []);

  return (
    <Layout title="Field map" subtitle="Flagged works plotted by inspection location">
      <div className="grid lg:grid-cols-[1fr_320px] gap-6">
        <div className="panel overflow-hidden h-[640px]">
          <MapContainer center={[25.8, 93.5]} zoom={6} className="h-full w-full">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {cases.map((c) => (
              <CircleMarker
                key={c.id}
                center={[c.location.latitude, c.location.longitude]}
                radius={RISK_RADIUS[c.risk_level]}
                pathOptions={{
                  color: RISK_COLOR[c.risk_level],
                  fillColor: RISK_COLOR[c.risk_level],
                  fillOpacity: 0.55,
                  weight: 1.5,
                }}
              >
                <Popup>
                  <div className="min-w-[200px]">
                    <p className="case-id mb-1">{c.case_number}</p>
                    <p className="text-sm font-medium text-ink-900 mb-1.5">{c.work_title}</p>
                    <p className="text-xs text-slate-600 mb-2">
                      {c.location.district}, {c.location.state}
                    </p>
                    <Link
                      to={`/risk-queue/${c.id}`}
                      className="text-xs text-ink-700 underline decoration-1 underline-offset-4"
                    >
                      Open case
                    </Link>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>

        <aside className="space-y-3">
          <div className="panel p-4">
            <p className="text-[11px] text-slate-500 mb-3">Legend</p>
            {(["critical", "high", "medium", "low"] as const).map((level) => (
              <div key={level} className="flex items-center gap-2.5 py-1.5">
                <span
                  className="w-2.5 h-2.5 rounded-full shrink-0"
                  style={{ backgroundColor: RISK_COLOR[level] }}
                />
                <span className="text-sm text-slate-600 capitalize">{level} risk</span>
              </div>
            ))}
          </div>

          <div className="max-h-[520px] overflow-y-auto space-y-2 pr-1">
            {cases.map((c) => (
              <Link
                key={c.id}
                to={`/risk-queue/${c.id}`}
                className="block panel p-3.5 hover:border-slate-300 transition-colors"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="case-id">{c.case_number}</span>
                  <RiskBadge level={c.risk_level} />
                </div>
                <p className="text-sm text-ink-900 leading-snug">{c.work_title}</p>
                <p className="text-xs text-slate-500 mt-1">
                  {c.location.district} · {formatINR(c.sanctioned_amount)}
                </p>
              </Link>
            ))}
          </div>
        </aside>
      </div>
    </Layout>
  );
}
