"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"job_seeker" | "employer">("job_seeker");
  const [err, setErr] = useState<string | null>(null);
  const router = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(`${base}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, role }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      setErr(body.detail || "Registration failed");
      return;
    }
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    router.push(role === "employer" ? "/dashboard/employer" : "/dashboard/seeker");
  }

  return (
    <div className="mx-auto max-w-md rounded-xl border border-stone-200 bg-white p-6 shadow-sm">
      <h1 className="text-xl font-bold">Register</h1>
      <form onSubmit={onSubmit} className="mt-4 space-y-3">
        <input
          type="email"
          required
          className="w-full rounded border border-stone-300 px-3 py-2"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          required
          minLength={8}
          className="w-full rounded border border-stone-300 px-3 py-2"
          placeholder="Password (min 8)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <select
          className="w-full rounded border border-stone-300 px-3 py-2"
          value={role}
          onChange={(e) => setRole(e.target.value as "job_seeker" | "employer")}
        >
          <option value="job_seeker">Job seeker</option>
          <option value="employer">Employer</option>
        </select>
        {err ? <p className="text-sm text-red-600">{String(err)}</p> : null}
        <button type="submit" className="w-full rounded-lg bg-brand py-2 font-semibold text-white hover:bg-brand-dark">
          Create account
        </button>
      </form>
    </div>
  );
}
