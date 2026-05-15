"use client";

import { DEMO_ADMIN, DEMO_EMPLOYER, DEMO_SEEKER } from "@/lib/constants";

type Props = { compact?: boolean };

export function DemoCredentials({ compact }: Props) {
  const cards = [
    {
      title: "Featured candidate",
      highlight: true,
      email: DEMO_SEEKER.email,
      password: DEMO_SEEKER.password,
      hint: `${DEMO_SEEKER.name} — full profile, applications & job alerts`,
    },
    {
      title: "Employer dashboard",
      email: DEMO_EMPLOYER.email,
      password: DEMO_EMPLOYER.password,
      hint: "Post jobs, view ranked applicants, analytics",
    },
    {
      title: "Admin",
      email: DEMO_ADMIN.email,
      password: DEMO_ADMIN.password,
      hint: "User & job oversight",
    },
  ];

  return (
    <div className={compact ? "space-y-3" : "grid gap-4 sm:grid-cols-3"}>
      {cards.map((c) => (
        <div
          key={c.email}
          className={`rounded-xl border p-4 text-sm ${
            c.highlight
              ? "border-brand bg-teal-50/80 shadow-sm ring-1 ring-brand/20"
              : "border-stone-200 bg-white"
          }`}
        >
          <p className="font-semibold text-stone-900">{c.title}</p>
          <p className="mt-2 font-mono text-xs text-stone-700">
            <span className="text-stone-500">Email </span>
            {c.email}
          </p>
          <p className="mt-1 font-mono text-xs text-stone-700">
            <span className="text-stone-500">Password </span>
            {c.password}
          </p>
          <p className="mt-2 text-xs text-stone-600">{c.hint}</p>
        </div>
      ))}
    </div>
  );
}
