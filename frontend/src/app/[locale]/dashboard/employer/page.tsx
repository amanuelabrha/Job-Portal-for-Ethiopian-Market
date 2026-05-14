"use client";

import { useEffect, useState } from "react";

export default function EmployerDashboard() {
  const [data, setData] = useState<string>("Loading…");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    if (!token) {
      setData("Please login as employer.");
      return;
    }
    void (async () => {
      const res = await fetch(`${base}/api/v1/employer/company`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        setData("Could not load company (wrong role or expired token).");
        return;
      }
      const c = await res.json();
      setData(`${c.name}`);
    })();
  }, []);

  return (
    <div className="rounded-xl border border-stone-200 bg-white p-6 shadow-sm">
      <h1 className="text-xl font-bold">Employer dashboard</h1>
      <p className="mt-2 text-stone-700">{data}</p>
      <p className="mt-4 text-sm text-stone-500">Post jobs via POST /api/v1/employer/jobs — see README for full API.</p>
    </div>
  );
}
