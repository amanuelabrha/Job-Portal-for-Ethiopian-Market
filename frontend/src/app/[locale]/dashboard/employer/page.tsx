"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";
import { useAuth } from "@/components/AuthProvider";
import { apiFetch } from "@/lib/api";
import { formatEtbRange } from "@/lib/format";
import { cardClass, btnPrimary, btnSecondary, Select, PageHeader, Badge, Spinner } from "@/components/ui";

interface Company {
  name: string;
  description?: string;
  website?: string;
  verified: boolean;
}

interface Job {
  id: number;
  title_en: string;
  city: string;
  view_count: number;
  application_count: number;
  salary_min_etb?: number;
  salary_max_etb?: number;
}

interface Applicant {
  application_id: number;
  seeker_user_id: number;
  full_name: string;
  email?: string;
  match_score?: number;
  status: string;
}

interface Analytics {
  total_views: number;
  total_applications: number;
  conversion_rate: number;
}

export default function EmployerDashboard() {
  const t = useTranslations("dashboard");
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [company, setCompany] = useState<Company | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [applicants, setApplicants] = useState<Applicant[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);

  const loadApplicants = useCallback(async (jobId: number) => {
    const [apps, an] = await Promise.all([
      apiFetch<Applicant[]>(`/api/v1/employer/jobs/${jobId}/applicants`),
      apiFetch<Analytics>(`/api/v1/employer/jobs/${jobId}/analytics`),
    ]);
    setApplicants(apps);
    setAnalytics(an);
  }, []);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push("/login");
      return;
    }
    if (user.role !== "employer") {
      router.push(user.role === "job_seeker" ? "/dashboard/seeker" : "/jobs");
      return;
    }
    void (async () => {
      try {
        const c = await apiFetch<Company>("/api/v1/employer/company");
        const j = await apiFetch<Job[]>("/api/v1/employer/jobs");
        setCompany(c);
        setJobs(j);
        if (j.length > 0) {
          setSelectedJobId(j[0].id);
        }
      } catch {
        setCompany(null);
      } finally {
        setLoading(false);
      }
    })();
  }, [user, authLoading, router, loadApplicants]);

  useEffect(() => {
    if (selectedJobId) void loadApplicants(selectedJobId);
  }, [selectedJobId, loadApplicants]);

  async function updateStatus(applicationId: number, status: "shortlisted" | "rejected") {
    await apiFetch(`/api/v1/employer/applications/${applicationId}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    if (selectedJobId) await loadApplicants(selectedJobId);
  }

  if (authLoading || loading) {
    return (
      <div className="flex justify-center py-20">
        <Spinner />
      </div>
    );
  }

  if (!company) {
    return (
      <div className={cardClass}>
        <p>Use employer demo: employer@ethiojobs.et / Employer123!</p>
        <Link href="/login" className="text-brand underline">
          Login
        </Link>
      </div>
    );
  }

  const selectedJob = jobs.find((j) => j.id === selectedJobId);

  return (
    <div className="space-y-8">
      <PageHeader title={t("employerTitle")} subtitle={company.name} />

      <div className={cardClass}>
        {company.verified ? <Badge variant="success">Verified employer</Badge> : null}
        <p className="mt-3 text-stone-700">{company.description}</p>
        {company.website ? (
          <a href={company.website} target="_blank" rel="noreferrer" className="mt-2 inline-block text-sm text-brand underline">
            {company.website}
          </a>
        ) : null}
      </div>

      {analytics ? (
        <div className="grid gap-4 sm:grid-cols-3">
          <Metric label={t("views")} value={String(analytics.total_views)} />
          <Metric label={t("applications")} value={String(analytics.total_applications)} />
          <Metric label={t("conversion")} value={`${(analytics.conversion_rate * 100).toFixed(1)}%`} />
        </div>
      ) : null}

      <section className={cardClass}>
        <h2 className="text-lg font-bold">{t("yourJobs")}</h2>
        <ul className="mt-4 max-h-64 divide-y divide-stone-100 overflow-y-auto">
          {jobs.map((j) => (
            <li key={j.id}>
              <button
                type="button"
                onClick={() => setSelectedJobId(j.id)}
                className={`w-full py-3 text-left transition ${selectedJobId === j.id ? "bg-teal-50" : "hover:bg-stone-50"}`}
              >
                <p className="font-medium text-stone-900">{j.title_en}</p>
                <p className="text-sm text-stone-500">
                  {j.city} · {formatEtbRange(j.salary_min_etb, j.salary_max_etb)} · {j.application_count} applicants
                </p>
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section className={cardClass}>
        <h2 className="text-lg font-bold">
          {t("applicants")} {selectedJob ? `— ${selectedJob.title_en}` : ""}
        </h2>
        <p className="text-sm text-stone-500">{t("rankedBy")}</p>
        {!selectedJobId ? <p className="mt-4 text-stone-500">{t("selectJob")}</p> : null}
        <ul className="mt-4 space-y-3">
          {applicants.map((a, i) => (
            <li key={a.application_id} className="rounded-xl border border-stone-100 bg-stone-50 p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-stone-900">
                    #{i + 1} {a.full_name}
                    {a.match_score != null && a.match_score > 0.6 ? (
                      <span className="ml-2">
                        <Badge variant="brand">Top match</Badge>
                      </span>
                    ) : null}
                  </p>
                  <p className="text-xs text-stone-500">{a.email}</p>
                  <p className="mt-1 text-sm font-medium text-brand">
                    {a.match_score != null ? `${(a.match_score * 100).toFixed(0)}% match` : "—"}
                  </p>
                  <Badge variant="default">{a.status}</Badge>
                </div>
                <div className="flex flex-col gap-2 sm:flex-row">
                  <button type="button" className={btnPrimary} onClick={() => void updateStatus(a.application_id, "shortlisted")}>
                    {t("shortlist")}
                  </button>
                  <button type="button" className={btnSecondary} onClick={() => void updateStatus(a.application_id, "rejected")}>
                    {t("reject")}
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
        {applicants.length === 0 && selectedJobId ? <p className="mt-4 text-stone-500">No applicants yet.</p> : null}
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-stone-200 bg-white p-5 text-center shadow-sm">
      <p className="text-2xl font-bold text-brand">{value}</p>
      <p className="mt-1 text-sm text-stone-600">{label}</p>
    </div>
  );
}
