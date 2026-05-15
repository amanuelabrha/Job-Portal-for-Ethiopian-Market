import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { DemoCredentials } from "@/components/DemoCredentials";
import { formatEtbRange } from "@/lib/format";
import { API_BASE } from "@/lib/constants";
import { cardClass } from "@/components/ui";

async function fetchJobs() {
  const res = await fetch(`${API_BASE}/api/v1/jobs?page_size=50`, { next: { revalidate: 30 } });
  if (!res.ok) return [];
  return res.json();
}

export default async function HomePage() {
  const t = await getTranslations("home");
  const jobs = await fetchJobs();

  return (
    <section className="space-y-12">
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand via-teal-700 to-brand-dark px-6 py-12 text-white shadow-xl sm:px-10 sm:py-14">
        <div className="relative z-10 max-w-2xl">
          <p className="text-sm font-medium uppercase tracking-wider text-teal-100">Ethiopia · ETB · Amharic</p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">{t("hero")}</h1>
          <p className="mt-4 text-lg text-teal-50/95">{t("sub")}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/jobs" className="rounded-xl bg-white px-6 py-3 text-sm font-semibold text-brand shadow-lg hover:bg-stone-50">
              {t("ctaJobs")}
            </Link>
            <Link href="/login" className="rounded-xl border-2 border-white/50 px-6 py-3 text-sm font-semibold text-white hover:bg-white/10">
              {t("ctaLogin")}
            </Link>
          </div>
        </div>
        <div className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
      </div>

      <div>
        <h2 className="text-xl font-bold text-stone-900">{t("demoTitle")}</h2>
        <p className="mt-1 text-stone-600">{t("demoSub")}</p>
        <div className="mt-5">
          <DemoCredentials />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label={t("statJobs")} value={jobs.length > 0 ? String(jobs.length) : "—"} />
        <StatCard label={t("statCities")} value="10+" />
        <StatCard label={t("statCurrency")} value="ETB" />
      </div>

      <div>
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-xl font-bold text-stone-900">{t("featuredJobs")}</h2>
          <Link href="/jobs" className="text-sm font-semibold text-brand hover:underline">
            {t("viewAll")}
          </Link>
        </div>
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {jobs.slice(0, 6).map(
            (j: {
              id: number;
              title_en: string;
              company_name: string;
              city: string;
              salary_min_etb?: number;
              salary_max_etb?: number;
              is_premium: boolean;
            }) => (
              <li key={j.id} className={`${cardClass} transition hover:border-brand/30 hover:shadow-md`}>
                <Link href={`/jobs/${j.id}`}>
                  <p className="text-xs font-medium text-stone-500">
                    {j.company_name} · {j.city}
                    {j.is_premium ? " · Premium" : ""}
                  </p>
                  <h3 className="mt-2 font-semibold text-stone-900">{j.title_en}</h3>
                  <p className="mt-2 text-sm font-medium text-brand">{formatEtbRange(j.salary_min_etb, j.salary_max_etb)}</p>
                </Link>
              </li>
            )
          )}
        </ul>
      </div>
    </section>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className={`${cardClass} text-center`}>
      <p className="text-3xl font-bold text-brand">{value}</p>
      <p className="mt-1 text-sm text-stone-600">{label}</p>
    </div>
  );
}
