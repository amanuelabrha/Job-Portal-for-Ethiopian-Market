import { NextIntlClientProvider } from "next-intl";
import { getMessages, getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { routing } from "@/i18n/routing";
import { Providers } from "@/components/Providers";
import { SiteHeader } from "@/components/SiteHeader";

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const { locale } = params;
  if (!routing.locales.includes(locale as "en" | "am")) {
    notFound();
  }
  setRequestLocale(locale);
  const messages = await getMessages();
  const footer = await getTranslations("footer");

  return (
    <NextIntlClientProvider messages={messages}>
      <Providers locale={locale}>
        <SiteHeader locale={locale} />
        <main className="mx-auto max-w-5xl px-4 py-8">{children}</main>
        <footer className="border-t border-stone-200 bg-white px-4 py-6 text-center text-sm text-stone-600">
          <p>{footer("note")}</p>
        </footer>
      </Providers>
    </NextIntlClientProvider>
  );
}
