"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";
import { useAuth } from "@/components/AuthProvider";
import { apiFetch } from "@/lib/api";
import { cardClass, btnPrimary, btnSecondary, Input, PageHeader, Badge, Spinner } from "@/components/ui";

interface Profile {
  full_name: string;
  headline: string;
  bio?: string;
  skills: string[];
  portfolio_urls: string[];
}

interface Application {
  id: number;
  job_id: number;
  status: string;
  match_score?: number;
  job_title?: string;
  created_at: string;
}

interface Alert {
  id: number;
  name: string;
  criteria: Record<string, unknown>;
  notify_email: boolean;
  notify_sms: boolean;
}

export default function SeekerDashboard() {
  const t = useTranslations("dashboard");
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [form, setForm] = useState({ full_name: "", headline: "", bio: "" });
  const [apps, setApps] = useState<Application[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [saveMsg, setSaveMsg] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [p, a, al] = await Promise.all([
        apiFetch<Profile>("/api/v1/seeker/profile"),
        apiFetch<Application[]>("/api/v1/seeker/applications"),
        apiFetch<Alert[]>("/api/v1/seeker/job-alerts"),
      ]);
      setProfile(p);
      setForm({ full_name: p.full_name, headline: p.headline, bio: p.bio || "" });
      setApps(a);
      setAlerts(al);
    } catch {
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push("/login");
      return;
    }
    if (user.role !== "job_seeker") {
      router.push(user.role === "employer" ? "/dashboard/employer" : "/jobs");
      return;
    }
    void load();
  }, [user, authLoading, router, load]);

  async function saveProfile() {
    try {
      const updated = await apiFetch<Profile>("/api/v1/seeker/profile", {
        method: "PATCH",
        body: JSON.stringify(form),
      });
      setProfile(updated);
      setEditMode(false);
      setSaveMsg(t("saved"));
      setTimeout(() => setSaveMsg(""), 3000);
    } catch (e) {
      setSaveMsg(e instanceof Error ? e.message : "Save failed");
    }
  }

  const statusVariant = (s: string): "default" | "success" | "warn" | "brand" => {
    if (s === "shortlisted" || s === "hired") return "success";
    if (s === "rejected") return "warn";
    if (s === "submitted") return "brand";
    return "default";
  };

  if (authLoading || loading) {
    return (
      <div className="flex justify-center py-20">
        <Spinner />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className={cardClass}>
        <p>Could not load profile.</p>
        <Link href="/login" className="text-brand underline">
          Sign in
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader title={t("seekerTitle")} subtitle={user?.email || ""} />

      <div className={`${cardClass} border-brand/20 bg-gradient-to-br from-teal-50/80 to-white`}>
        {!editMode ? (
          <>
            <h2 className="text-xl font-bold text-stone-900">{profile.full_name}</h2>
            <p className="text-stone-600">{profile.headline}</p>
            {profile.bio ? <p className="mt-3 text-sm text-stone-700">{profile.bio}</p> : null}
            <div className="mt-4 flex flex-wrap gap-2">
              {profile.skills.map((s) => (
                <Badge key={s} variant="brand">
                  {s}
                </Badge>
              ))}
            </div>
            <button type="button" className={`${btnSecondary} mt-4`} onClick={() => setEditMode(true)}>
              {t("editProfile")}
            </button>
          </>
        ) : (
          <div className="space-y-3">
            <Input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} placeholder="Full name" />
            <Input value={form.headline} onChange={(e) => setForm({ ...form, headline: e.target.value })} placeholder="Headline" />
            <textarea
              className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm"
              rows={4}
              value={form.bio}
              onChange={(e) => setForm({ ...form, bio: e.target.value })}
              placeholder="Bio"
            />
            <div className="flex gap-2">
              <button type="button" className={btnPrimary} onClick={() => void saveProfile()}>
                {t("saveProfile")}
              </button>
              <button type="button" className={btnSecondary} onClick={() => setEditMode(false)}>
                Cancel
              </button>
            </div>
          </div>
        )}
        {saveMsg ? <p className="mt-2 text-sm text-emerald-700">{saveMsg}</p> : null}
      </div>

      <section className={cardClass}>
        <h2 className="text-lg font-bold">{t("myApplications")}</h2>
        <ul className="mt-4 divide-y divide-stone-100">
          {apps.map((a) => (
            <li key={a.id} className="flex flex-wrap items-center justify-between gap-2 py-4">
              <div>
                <Link href={`/jobs/${a.job_id}`} className="font-medium text-brand hover:underline">
                  {a.job_title || `Job #${a.job_id}`}
                </Link>
                <p className="text-xs text-stone-500">{new Date(a.created_at).toLocaleDateString("en-ET")}</p>
              </div>
              <div className="flex items-center gap-2">
                {a.match_score != null ? (
                  <span className="text-xs font-medium text-stone-600">Match {(a.match_score * 100).toFixed(0)}%</span>
                ) : null}
                <Badge variant={statusVariant(a.status)}>{a.status}</Badge>
              </div>
            </li>
          ))}
        </ul>
        {apps.length === 0 ? <p className="text-sm text-stone-500">No applications yet.</p> : null}
      </section>

      <section className={cardClass}>
        <h2 className="text-lg font-bold">{t("jobAlerts")}</h2>
        <ul className="mt-4 space-y-3">
          {alerts.map((al) => (
            <li key={al.id} className="rounded-xl bg-stone-50 p-4 text-sm">
              <p className="font-semibold text-stone-900">{al.name}</p>
              <p className="mt-1 text-stone-600">
                {al.criteria.city ? `City: ${String(al.criteria.city)} · ` : ""}
                {al.criteria.category ? `Category: ${String(al.criteria.category)} · ` : ""}
                Email {al.notify_email ? "on" : "off"} · SMS {al.notify_sms ? "on" : "off"}
              </p>
            </li>
          ))}
        </ul>
      </section>

      <Link href="/jobs" className={btnPrimary}>
        {t("browseJobs")}
      </Link>
    </div>
  );
}
