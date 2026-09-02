import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import { RiskBadge } from "../components/Badge";
import { fetchInspections } from "../services/api";
import { InspectionTask } from "../types";
import { formatDate } from "../utils/format";

const STATUS_LABEL: Record<InspectionTask["status"], string> = {
  pending: "Pending",
  scheduled: "Scheduled",
  in_progress: "In progress",
  completed: "Completed",
};

const STATUS_STYLE: Record<InspectionTask["status"], string> = {
  pending: "border-slate-300 text-slate-500",
  scheduled: "border-ink-600 text-ink-700",
  in_progress: "border-ochre-400 text-ochre-600",
  completed: "border-moss-400 text-moss-500",
};

export default function InspectionPlan() {
  const [tasks, setTasks] = useState<InspectionTask[]>([]);
  const [checked, setChecked] = useState<Record<string, boolean>>({});

  useEffect(() => {
    fetchInspections().then((data) => {
      setTasks(data);
      const initial: Record<string, boolean> = {};
      data.forEach((t) => t.checklist.forEach((c) => (initial[c.id] = c.done)));
      setChecked(initial);
    });
  }, []);

  const toggle = (id: string) => setChecked((prev) => ({ ...prev, [id]: !prev[id] }));

  return (
    <Layout title="Inspection plan" subtitle={`${tasks.length} field inspections scheduled`}>
      <div className="space-y-5">
        {tasks.map((task) => {
          const done = task.checklist.filter((c) => checked[c.id]).length;
          const total = task.checklist.length;
          return (
            <div key={task.id} className="panel p-6">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-5">
                <div>
                  <div className="flex items-center gap-2 mb-1.5">
                    <RiskBadge level={task.priority} />
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-sm text-xs font-medium border ${STATUS_STYLE[task.status]}`}>
                      {STATUS_LABEL[task.status]}
                    </span>
                  </div>
                  <h3 className="font-serif text-lg text-ink-900">{task.work_title}</h3>
                  <p className="text-xs text-slate-500 mt-1">
                    {task.location.district}, {task.location.state} · Assigned to {task.assigned_to}
                  </p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-[11px] text-slate-500">Scheduled</p>
                  <p className="text-sm font-medium text-ink-900">{formatDate(task.scheduled_date)}</p>
                  <Link
                    to={`/risk-queue/${task.case_id}`}
                    className="text-xs text-ink-700 underline decoration-1 underline-offset-4 mt-1 inline-block"
                  >
                    View case {task.case_number}
                  </Link>
                </div>
              </div>

              <div className="divider pt-4">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-[11px] text-slate-500">Field checklist</p>
                  <p className="text-xs text-slate-500">{done}/{total} complete</p>
                </div>
                <div className="space-y-2">
                  {task.checklist.map((item) => (
                    <label
                      key={item.id}
                      className="flex items-center gap-3 text-sm text-ink-900 cursor-pointer select-none"
                    >
                      <input
                        type="checkbox"
                        checked={!!checked[item.id]}
                        onChange={() => toggle(item.id)}
                        className="w-4 h-4 rounded-sm border-slate-300 text-ink-900 focus:ring-ink-700"
                      />
                      <span className={checked[item.id] ? "line-through text-slate-500" : ""}>
                        {item.label}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Layout>
  );
}
