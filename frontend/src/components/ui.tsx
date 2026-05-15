import { forwardRef } from "react";

export function cn(...parts: (string | false | undefined)[]) {
  return parts.filter(Boolean).join(" ");
}

export const inputClass =
  "w-full rounded-lg border border-stone-300 bg-white px-3 py-2.5 text-sm text-stone-900 shadow-sm placeholder:text-stone-400 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20";

export const btnPrimary =
  "inline-flex items-center justify-center rounded-lg bg-brand px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-dark focus:outline-none focus:ring-2 focus:ring-brand/40 disabled:cursor-not-allowed disabled:opacity-60";

export const btnSecondary =
  "inline-flex items-center justify-center rounded-lg border border-stone-300 bg-white px-4 py-2.5 text-sm font-medium text-stone-800 shadow-sm transition hover:bg-stone-50 focus:outline-none focus:ring-2 focus:ring-stone-200";

export const cardClass = "rounded-2xl border border-stone-200 bg-white p-6 shadow-sm";

export const PageHeader = ({ title, subtitle }: { title: string; subtitle?: string }) => (
  <header className="mb-8">
    <h1 className="text-2xl font-bold tracking-tight text-stone-900 sm:text-3xl">{title}</h1>
    {subtitle ? <p className="mt-2 max-w-2xl text-stone-600">{subtitle}</p> : null}
  </header>
);

export const Spinner = () => (
  <span className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-brand border-t-transparent" />
);

export const Badge = ({ children, variant = "default" }: { children: React.ReactNode; variant?: "default" | "success" | "warn" | "brand" }) => {
  const styles = {
    default: "bg-stone-100 text-stone-800",
    success: "bg-emerald-100 text-emerald-800",
    warn: "bg-amber-100 text-amber-900",
    brand: "bg-teal-100 text-teal-900",
  };
  return <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium", styles[variant])}>{children}</span>;
};

export const Button = forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "ghost" }
>(function Button({ className, variant = "primary", children, ...props }, ref) {
  const base =
    variant === "primary" ? btnPrimary : variant === "secondary" ? btnSecondary : "text-sm font-medium text-stone-700 hover:text-brand";
  return (
    <button ref={ref} className={cn(base, className)} {...props}>
      {children}
    </button>
  );
});

export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(function Input(
  { className, ...props },
  ref
) {
  return <input ref={ref} className={cn(inputClass, className)} {...props} />;
});

export const Select = forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(function Select(
  { className, children, ...props },
  ref
) {
  return (
    <select ref={ref} className={cn(inputClass, className)} {...props}>
      {children}
    </select>
  );
});
