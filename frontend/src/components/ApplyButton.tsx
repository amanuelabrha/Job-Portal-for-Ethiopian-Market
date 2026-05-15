"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { useAuth } from "@/components/AuthProvider";
import { apiFetch } from "@/lib/api";
import { btnPrimary } from "@/components/ui";
import { cn } from "@/components/ui";

export function ApplyButton({ jobId }: { jobId: number }) {
  const t = useTranslations("jobs");
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "err">("idle");
  const [msg, setMsg] = useState("");
  const router = useRouter();
  const { user, loading } = useAuth();

  async function apply() {
    if (!user) {
      router.push("/login");
      return;
    }
    if (user.role !== "job_seeker") {
      setStatus("err");
      setMsg(t("employerCannotApply"));
      return;
    }
    setStatus("loading");
    setMsg("");
    try {
      await apiFetch(`/api/v1/jobs/${jobId}/apply`, {
        method: "POST",
        body: JSON.stringify({
          use_profile_resume: true,
          cover_letter: "I am interested in this position and available to start in Addis Ababa.",
        }),
      });
      setStatus("ok");
      setMsg(t("applySuccess"));
    } catch (e) {
      setStatus("err");
      setMsg(e instanceof Error ? e.message : "Could not apply");
    }
  }

  if (loading) return null;

  return (
    <div className="flex flex-wrap items-center gap-3">
      <button
        type="button"
        onClick={() => void apply()}
        disabled={status === "loading" || status === "ok"}
        className={cn(btnPrimary, "px-8")}
      >
        {status === "loading" ? "…" : status === "ok" ? `✓ ${t("applied")}` : t("apply")}
      </button>
      {!user ? <p className="text-sm text-stone-500">{t("loginToApply")}</p> : null}
      {msg ? <p className={`text-sm ${status === "err" ? "text-red-600" : "text-emerald-700"}`}>{msg}</p> : null}
    </div>
  );
}
