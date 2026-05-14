import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { formatEtbRange } from "@/lib/format";

interface JobOut {
  id: number;
  company_name: string;
  title_en: string;
  title_am?: string | null;
  city: string;
  salary_min_etb?: number | null;
  salary_max_etb?: number | null;
  job_type: string;
  is_premium: boolean;
}

async function fetchJobs(): Promise<JobOut[]> {
  const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${base}/api/v1/jobs?page_size=30`, { next: { revalidate: 60 } });
  if (!res.ok) return [];
  return res.json();
}

export default async function JobsPage() {
  const t = await getTranslations("jobs");
  const jobs = await fetchJobs();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-stone-900">{t("title")}</h1>
      <ul className="grid gap-4 sm:grid-cols-2">
        {jobs.map((j) => (
          <li
            key={j.id}
            className="rounded-xl border border-stone-200 bg-white p-4 shadow-sm transition hover:border-brand/40"
          >
            <Link href={`/jobs/${j.id}`} className="block">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h2 className="font-semibold text-stone-900">{j.title_en}</h2>
                  {j.title_am ? (
                    <p className="text-sm text-stone-600" dir="ltr">
                      {j.title_am}
                    </p>
                  ) : null}
                  <p className="mt-1 text-sm text-stone-500">
                    {j.company_name} · {j.city}
                  </p>
                </div>
                {j.is_premium ? (
                  <span className="shrink-0 rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-900">
                    Premium
                  </span>
                ) : null}
              </div>
              <p className="mt-2 text-sm text-stone-600">
                {t("salary")}: {formatEtbRange(j.salary_min_etb, j.salary_max_etb)} · {t("type")}: {j.job_type}
              </p>
            </Link>
          </li>
        ))}
      </ul>
      {jobs.length === 0 ? (
        <p className="text-stone-500">No jobs yet — start the API and run the seed script.</p>
      ) : null}
    </div>
  );
}
