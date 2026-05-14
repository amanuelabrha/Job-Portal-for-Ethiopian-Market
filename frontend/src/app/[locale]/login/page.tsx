"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const router = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(`${base}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      setErr("Login failed");
      return;
    }
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    router.push("/dashboard/seeker");
  }

  return (
    <div className="mx-auto max-w-md rounded-xl border border-stone-200 bg-white p-6 shadow-sm">
      <h1 className="text-xl font-bold">Login</h1>
      <p className="mt-1 text-sm text-stone-500">Use seeker@ethiojobs.et / Seeker123! after seed.</p>
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
          className="w-full rounded border border-stone-300 px-3 py-2"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {err ? <p className="text-sm text-red-600">{err}</p> : null}
        <button type="submit" className="w-full rounded-lg bg-brand py-2 font-semibold text-white hover:bg-brand-dark">
          Sign in
        </button>
      </form>
    </div>
  );
}
