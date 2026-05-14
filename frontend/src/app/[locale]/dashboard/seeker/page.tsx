"use client";

import { useEffect, useState } from "react";

export default function SeekerDashboard() {
  const [data, setData] = useState<string>("Loading…");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    if (!token) {
      setData("Please login first.");
      return;
    }
    void (async () => {
      const res = await fetch(`${base}/api/v1/seeker/profile`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        setData("Could not load profile (wrong role or expired token).");
        return;
      }
      const p = await res.json();
      setData(`${p.full_name} — ${p.headline}`);
    })();
  }, []);

  return (
    <div className="rounded-xl border border-stone-200 bg-white p-6 shadow-sm">
      <h1 className="text-xl font-bold">Seeker dashboard</h1>
      <p className="mt-2 text-stone-700">{data}</p>
      <p className="mt-4 text-sm text-stone-500">
        Upload resume via POST /api/v1/seeker/resume (multipart) from API client or extend this UI.
      </p>
    </div>
  );
}
