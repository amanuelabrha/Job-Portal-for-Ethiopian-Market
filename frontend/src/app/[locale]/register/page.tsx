"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";
import { register } from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";
import { cardClass, btnPrimary, Input, Select, PageHeader } from "@/components/ui";

export default function RegisterPage() {
  const t = useTranslations("auth");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"job_seeker" | "employer">("job_seeker");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { refresh, setUser } = useAuth();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const me = await register(email, password, role);
      setUser(me);
      await refresh();
      router.push(role === "employer" ? "/dashboard/employer" : "/dashboard/seeker");
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md space-y-6">
      <PageHeader title={t("createAccount")} subtitle={t("signInSub")} />
      <div className={cardClass}>
        <form onSubmit={(e) => void onSubmit(e)} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-stone-700">Email</label>
            <Input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-stone-700">Password</label>
            <Input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-stone-700">I am a</label>
            <Select value={role} onChange={(e) => setRole(e.target.value as "job_seeker" | "employer")}>
              <option value="job_seeker">{t("roleSeeker")}</option>
              <option value="employer">{t("roleEmployer")}</option>
            </Select>
          </div>
          {err ? <p className="text-sm text-red-600">{err}</p> : null}
          <button type="submit" disabled={loading} className={`${btnPrimary} w-full`}>
            {loading ? t("creating") : t("createAccount")}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-stone-600">
          {t("haveAccount")}{" "}
          <Link href="/login" className="font-medium text-brand hover:underline">
            {t("signIn")}
          </Link>
        </p>
      </div>
    </div>
  );
}
