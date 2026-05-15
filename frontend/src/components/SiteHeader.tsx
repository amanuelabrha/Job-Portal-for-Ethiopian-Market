"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Link, usePathname, useRouter } from "@/i18n/navigation";
import { useAuth } from "@/components/AuthProvider";
import { cn, btnPrimary, btnSecondary } from "@/components/ui";

export function SiteHeader({ locale }: { locale: string }) {
  const t = useTranslations("nav");
  const { user, loading, signOut } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);

  function handleLogout() {
    signOut();
    setMenuOpen(false);
    router.push("/");
    router.refresh();
  }

  const navLink = (href: string, label: string) => (
    <Link
      href={href}
      onClick={() => setMenuOpen(false)}
      className={cn(
        "rounded-lg px-3 py-2 text-sm font-medium transition",
        pathname === href || pathname?.startsWith(href + "/")
          ? "bg-teal-50 text-brand"
          : "text-stone-700 hover:bg-stone-100 hover:text-brand"
      )}
    >
      {label}
    </Link>
  );

  const dashboardHref =
    user?.role === "employer" ? "/dashboard/employer" : user?.role === "admin" ? "/jobs" : "/dashboard/seeker";

  return (
    <header className="sticky top-0 z-50 border-b border-stone-200/80 bg-white/90 shadow-sm backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        <Link href="/" className="flex shrink-0 items-center gap-2" onClick={() => setMenuOpen(false)}>
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand text-sm font-bold text-white">
            EJ
          </span>
          <span className="text-lg font-bold tracking-tight text-stone-900">
            Ethio<span className="text-brand">Jobs</span>
          </span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden items-center gap-1 md:flex">
          {navLink("/jobs", t("jobs"))}
          {!loading && !user && (
            <>
              {navLink("/login", t("login"))}
              <Link href="/register" className={cn(btnPrimary, "ml-2 !py-2")}>
                {t("register")}
              </Link>
            </>
          )}
          {!loading && user && (
            <>
              {navLink(dashboardHref, t("dashboard"))}
              {user.role === "job_seeker" && navLink("/dashboard/employer", t("employer"))}
              {user.role === "employer" && navLink("/jobs", t("jobs"))}
              <div className="ml-2 flex items-center gap-2 border-l border-stone-200 pl-3">
                <div className="hidden text-right lg:block">
                  <p className="max-w-[140px] truncate text-xs font-medium text-stone-900">{user.email}</p>
                  <p className="text-[10px] uppercase tracking-wide text-stone-500">{user.role.replace("_", " ")}</p>
                </div>
                <button type="button" onClick={handleLogout} className={cn(btnSecondary, "!py-2 text-xs")}>
                  {t("logout")}
                </button>
              </div>
            </>
          )}
        </nav>

        {/* Locale + mobile toggle */}
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-stone-200 bg-stone-50 p-0.5 text-xs font-semibold">
            <Link
              href={pathname || "/"}
              locale="en"
              className={cn("rounded-md px-2.5 py-1.5 transition", locale === "en" ? "bg-white text-brand shadow-sm" : "text-stone-500")}
            >
              EN
            </Link>
            <Link
              href={pathname || "/"}
              locale="am"
              className={cn("rounded-md px-2.5 py-1.5 transition", locale === "am" ? "bg-white text-brand shadow-sm" : "text-stone-500")}
            >
              አማ
            </Link>
          </div>
          <button
            type="button"
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-stone-200 text-stone-700 md:hidden"
            aria-label="Menu"
            onClick={() => setMenuOpen((o) => !o)}
          >
            {menuOpen ? (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen ? (
        <div className="border-t border-stone-100 bg-white px-4 py-4 md:hidden">
          <nav className="flex flex-col gap-1">
            {navLink("/jobs", t("jobs"))}
            {!loading && !user && (
              <>
                {navLink("/login", t("login"))}
                <Link href="/register" className={cn(btnPrimary, "mt-2 text-center")} onClick={() => setMenuOpen(false)}>
                  {t("register")}
                </Link>
              </>
            )}
            {!loading && user && (
              <>
                {navLink(dashboardHref, t("dashboard"))}
                <p className="px-3 py-2 text-xs text-stone-500">{user.email}</p>
                <button type="button" onClick={handleLogout} className={cn(btnSecondary, "mt-2 w-full")}>
                  {t("logout")}
                </button>
              </>
            )}
          </nav>
        </div>
      ) : null}
    </header>
  );
}
