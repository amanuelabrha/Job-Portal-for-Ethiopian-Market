"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";
import { login } from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";
import { DEMO_SEEKER } from "@/lib/constants";
import { DemoCredentials } from "@/components/DemoCredentials";
import { cardClass, btnPrimary, Input, PageHeader } from "@/components/ui";

export default function LoginPage() {
  const t = useTranslations("auth");
  const [email, setEmail] = useState(DEMO_SEEKER.email);
  const [password, setPassword] = useState(DEMO_SEEKER.password);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { refresh, setUser } = useAuth();

  async function doLogin(e: React.FormEvent, em?: string, pw?: string) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const me = await login(em ?? email, pw ?? password);
      setUser(me);
      await refresh();
      if (me.role === "employer") router.push("/dashboard/employer");
      else if (me.role === "admin") router.push("/jobs");
      else router.push("/dashboard/seeker");
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg space-y-8">
      <PageHeader title={t("signIn")} subtitle={t("signInSub")} />
      <div className={cardClass}>
        <form onSubmit={(e) => void doLogin(e)} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-stone-700">Email</label>
            <Input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-stone-700">Password</label>
            <Input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          {err ? <p className="text-sm text-red-600">{err}</p> : null}
          <button type="submit" disabled={loading} className={`${btnPrimary} w-full`}>
            {loading ? t("signingIn") : t("signIn")}
          </button>
        </form>
        <button
          type="button"
          className="mt-4 w-full rounded-lg border border-brand/30 bg-teal-50 py-2.5 text-sm font-medium text-brand hover:bg-teal-100"
          disabled={loading}
          onClick={(e) => {
            setEmail(DEMO_SEEKER.email);
            setPassword(DEMO_SEEKER.password);
            void doLogin(e, DEMO_SEEKER.email, DEMO_SEEKER.password);
          }}
        >
          {t("quickLogin")} {DEMO_SEEKER.name}
        </button>
        <p className="mt-4 text-center text-sm text-stone-600">
          {t("noAccount")}{" "}
          <Link href="/register" className="font-medium text-brand hover:underline">
            {t("createAccount")}
          </Link>
        </p>
      </div>
      <DemoCredentials />
    </div>
  );
}
