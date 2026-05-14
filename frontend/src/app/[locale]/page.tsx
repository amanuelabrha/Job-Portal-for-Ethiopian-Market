import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";

export default async function HomePage() {
  const t = await getTranslations("home");
  const tm = await getTranslations("meta");
  return (
    <section className="space-y-8">
      <div className="rounded-2xl bg-gradient-to-br from-brand to-brand-dark p-8 text-white shadow-lg">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">{t("hero")}</h1>
        <p className="mt-4 max-w-2xl text-lg text-teal-50">{t("sub")}</p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="/jobs"
            className="rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-brand shadow hover:bg-stone-100"
          >
            {t("ctaJobs")}
          </Link>
          <Link
            href="/register"
            className="rounded-lg border border-white/40 px-5 py-2.5 text-sm font-semibold text-white hover:bg-white/10"
          >
            {t("ctaRegister")}
          </Link>
        </div>
      </div>
      <p className="text-sm text-stone-500">{tm("description")}</p>
    </section>
  );
}
