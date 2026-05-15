"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";

export function SiteFooter() {
  const t = useTranslations("footer");
  const nav = useTranslations("nav");

  return (
    <footer className="mt-auto border-t border-stone-200 bg-stone-900 text-stone-300">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <div className="grid gap-8 sm:grid-cols-3">
          <div>
            <p className="text-lg font-bold text-white">EthioJobs</p>
            <p className="mt-2 text-sm text-stone-400">{t("tagline")}</p>
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-stone-500">{t("links")}</p>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <Link href="/jobs" className="hover:text-white">
                  {nav("jobs")}
                </Link>
              </li>
              <li>
                <Link href="/login" className="hover:text-white">
                  {nav("login")}
                </Link>
              </li>
              <li>
                <Link href="/register" className="hover:text-white">
                  {nav("register")}
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-stone-500">{t("locale")}</p>
            <p className="mt-3 text-sm">{t("note")}</p>
          </div>
        </div>
        <p className="mt-8 border-t border-stone-800 pt-6 text-center text-xs text-stone-500">
          © {new Date().getFullYear()} EthioJobs · {t("rights")}
        </p>
      </div>
    </footer>
  );
}
