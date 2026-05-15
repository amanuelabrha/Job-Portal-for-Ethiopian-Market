"use client";

import { GoogleOAuthProvider } from "@react-oauth/google";
import { useEffect } from "react";
import { AuthProvider } from "@/components/AuthProvider";

const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

export function Providers({ children, locale }: { children: React.ReactNode; locale: string }) {
  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.lang = locale;
    }
  }, [locale]);

  const inner = <AuthProvider>{children}</AuthProvider>;

  if (!clientId) {
    return inner;
  }
  return <GoogleOAuthProvider clientId={clientId}>{inner}</GoogleOAuthProvider>;
}
