import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ethiopia Job Portal",
  description: "Jobs for Ethiopia — ETB, Amharic, mobile-first.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html suppressHydrationWarning>
      <body className="min-h-screen bg-stone-50 text-stone-900 antialiased">{children}</body>
    </html>
  );
}
