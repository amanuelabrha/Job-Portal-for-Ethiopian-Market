"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { API_BASE, ETHIOPIAN_CITIES, JOB_CATEGORIES, JOB_TYPES } from "@/lib/constants";
import { formatEtbRange } from "@/lib/format";
import { inputClass, btnPrimary, Spinner, Badge } from "@/components/ui";

interface JobOut {
  id: number;
  company_name: string;
  title_en: string;
  title_am?: string | null;
  city: string;
  category: string;
  salary_min_etb?: number | null;
  salary_max_etb?: number | null;
  job_type: string;
  is_premium: boolean;
}

export function JobSearch() {
  const t = useTranslations("jobs");
  const [city, setCity] = useState("");
  const [category, setCategory] = useState("");
  const [jobType, setJobType] = useState("");
  const [q, setQ] = useState("");
  const [jobs, setJobs] = useState<JobOut[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const params = new URLSearchParams({ page_size: "50" });
    if (city) params.set("city", city);
    if (category) params.set("category", category);
    if (jobType) params.set("job_type", jobType);
    if (q.trim()) params.set("q", q.trim());
    try {
      const res = await fetch(`${API_BASE}/api/v1/jobs?${params}`);
      setJobs(res.ok ? await res.json() : []);
    } catch {
      setJobs([]);
    } finally {
      setLoading(false);
    }
  }, [city, category, jobType, q]);

  useEffect(() => {
    const id = setTimeout(() => void load(), 300);
    return () => clearTimeout(id);
  }, [load]);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm sm:p-5">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <input
            type="search"
            placeholder={t("searchPlaceholder")}
            className={`${inputClass} sm:col-span-2 lg:col-span-5`}
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <select className={inputClass} value={city} onChange={(e) => setCity(e.target.value)} aria-label={t("city")}>
            <option value="">{t("allCities")}</option>
            {ETHIOPIAN_CITIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <select className={inputClass} value={category} onChange={(e) => setCategory(e.target.value)} aria-label={t("category")}>
            <option value="">{t("allCategories")}</option>
            {JOB_CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <select className={inputClass} value={jobType} onChange={(e) => setJobType(e.target.value)} aria-label={t("type")}>
            <option value="">{t("allTypes")}</option>
            {JOB_TYPES.map((jt) => (
              <option key={jt} value={jt}>
                {jt.replace("_", " ")}
              </option>
            ))}
          </select>
          <button type="button" onClick={() => void load()} className={`${btnPrimary} w-full`}>
            {t("search")}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center gap-2 py-12 text-stone-500">
          <Spinner />
          {t("loading")}
        </div>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2">
          {jobs.map((j) => (
            <li
              key={j.id}
              className="group rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition hover:border-brand/30 hover:shadow-md"
            >
              <Link href={`/jobs/${j.id}`} className="block">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h2 className="font-semibold text-stone-900 group-hover:text-brand">{j.title_en}</h2>
                    {j.title_am ? <p className="mt-0.5 text-sm text-stone-600">{j.title_am}</p> : null}
                    <p className="mt-2 text-sm text-stone-500">
                      {j.company_name} · {j.city}
                    </p>
                  </div>
                  {j.is_premium ? <Badge variant="warn">Premium</Badge> : null}
                </div>
                <p className="mt-3 text-sm font-medium text-brand">
                  {formatEtbRange(j.salary_min_etb, j.salary_max_etb)}
                </p>
                <p className="mt-1 text-xs capitalize text-stone-500">
                  {j.category} · {j.job_type.replace("_", " ")}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
      {!loading && jobs.length === 0 ? <p className="py-8 text-center text-stone-500">{t("empty")}</p> : null}
    </div>
  );
}
