import { getTranslations } from "next-intl/server";
import { notFound } from "next/navigation";
import { formatEtbRange } from "@/lib/format";
import { ApplyButton } from "@/components/ApplyButton";
import { API_BASE } from "@/lib/constants";
import { cardClass } from "@/components/ui";
import { Link } from "@/i18n/navigation";

async function fetchJob(id: string) {
  const res = await fetch(`${API_BASE}/api/v1/jobs/${id}`, { next: { revalidate: 30 } });
  if (!res.ok) return null;
  return res.json();
}

export default async function JobDetailPage({ params }: { params: { locale: string; id: string } }) {
  const job = await fetchJob(params.id);
  if (!job) notFound();
  const t = await getTranslations("jobs");

  return (
    <div className="space-y-6">
      <Link href="/jobs" className="text-sm font-medium text-brand hover:underline">
        ← Back to jobs
      </Link>
      <article className={`${cardClass} space-y-6`}>
        <header className="border-b border-stone-100 pb-6">
          <p className="text-sm text-stone-500">
            {job.company_name} · {job.city} · {job.category}
            {job.is_premium ? (
              <span className="ml-2 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-900">Premium</span>
            ) : null}
          </p>
          <h1 className="mt-3 text-3xl font-bold text-stone-900">{job.title_en}</h1>
          {job.title_am ? (
            <h2 className="mt-2 text-xl text-stone-800" dir="ltr">
              {job.title_am}
            </h2>
          ) : null}
          <p className="mt-4 text-lg font-semibold text-brand">{formatEtbRange(job.salary_min_etb, job.salary_max_etb)}</p>
          <p className="mt-1 text-sm capitalize text-stone-600">{String(job.job_type).replace("_", " ")}</p>
          {job.view_count != null ? (
            <p className="mt-2 text-xs text-stone-400">
              {job.view_count} views · {job.application_count} applications
            </p>
          ) : null}
        </header>
        <ApplyButton jobId={job.id} />
        <section>
          <h3 className="text-lg font-semibold text-stone-900">Description</h3>
          <p className="mt-3 whitespace-pre-wrap leading-relaxed text-stone-700">{job.description_en}</p>
          {job.description_am ? (
            <p className="mt-4 whitespace-pre-wrap leading-relaxed text-stone-700" dir="ltr">
              {job.description_am}
            </p>
          ) : null}
        </section>
        <section>
          <h3 className="text-lg font-semibold text-stone-900">Requirements</h3>
          <p className="mt-3 whitespace-pre-wrap leading-relaxed text-stone-700">{job.requirements_en}</p>
        </section>
      </article>
    </div>
  );
}
