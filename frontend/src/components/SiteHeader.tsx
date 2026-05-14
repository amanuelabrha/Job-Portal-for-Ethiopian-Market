"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";

export function SiteHeader({ locale }: { locale: string }) {
  const t = useTranslations("nav");
  return (
    <header className="sticky top-0 z-20 border-b border-stone-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-4 py-3">
        <Link href="/" className="text-lg font-semibold text-brand">
          EthioJobs
        </Link>
        <nav className="flex flex-wrap items-center gap-3 text-sm font-medium">
          <Link href="/jobs" className="text-stone-700 hover:text-brand">
            {t("jobs")}
          </Link>
          <Link href="/login" className="text-stone-700 hover:text-brand">
            {t("login")}
          </Link>
          <Link href="/register" className="rounded-md bg-brand px-3 py-1.5 text-white hover:bg-brand-dark">
            {t("register")}
          </Link>
          <Link href="/dashboard/seeker" className="text-stone-700 hover:text-brand">
            {t("dashboard")}
          </Link>
          <Link href="/dashboard/employer" className="text-stone-700 hover:text-brand">
            {t("employer")}
          </Link>
        </nav>
        <div className="flex gap-1 text-xs">
          <Link href="/" locale="en" className={locale === "en" ? "font-bold text-brand" : "text-stone-500"}>
            EN
          </Link>
          <span className="text-stone-300">|</span>
          <Link href="/" locale="am" className={locale === "am" ? "font-bold text-brand" : "text-stone-500"}>
            አማ
          </Link>
        </div>
      </div>
    </header>
  );
}
