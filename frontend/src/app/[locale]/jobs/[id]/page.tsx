import { getTranslations } from "next-intl/server";
import { notFound } from "next/navigation";
import { formatEtbRange } from "@/lib/format";

async function fetchJob(id: string) {
  const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${base}/api/v1/jobs/${id}`, { next: { revalidate: 30 } });
  if (!res.ok) return null;
  return res.json();
}

export default async function JobDetailPage({ params }: { params: { locale: string; id: string } }) {
  const job = await fetchJob(params.id);
  if (!job) notFound();
  const t = await getTranslations("jobs");

  return (
    <article className="space-y-6 rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
      <header>
        <p className="text-sm text-stone-500">
          {job.company_name} · {job.city}
        </p>
        <h1 className="mt-2 text-3xl font-bold text-stone-900">{job.title_en}</h1>
        {job.title_am ? (
          <h2 className="mt-2 text-xl text-stone-800" dir="ltr">
            {job.title_am}
          </h2>
        ) : null}
        <p className="mt-3 text-sm text-stone-600">
          {t("salary")}: {formatEtbRange(job.salary_min_etb, job.salary_max_etb)} · {t("type")}: {job.job_type}
        </p>
      </header>
      <section>
        <h3 className="font-semibold text-stone-900">Description</h3>
        <p className="mt-2 whitespace-pre-wrap text-stone-700">{job.description_en}</p>
        {job.description_am ? (
          <p className="mt-4 whitespace-pre-wrap text-stone-700" dir="ltr">
            {job.description_am}
          </p>
        ) : null}
      </section>
      <section>
        <h3 className="font-semibold text-stone-900">Requirements</h3>
        <p className="mt-2 whitespace-pre-wrap text-stone-700">{job.requirements_en}</p>
      </section>
    </article>
  );
}
