/** ETB display — Ethiopian Birr; narrowSymbol may fall back on some runtimes. */
export function formatEtb(n?: number | null): string {
  if (n == null) return "—";
  try {
    return new Intl.NumberFormat("en-ET", {
      style: "currency",
      currency: "ETB",
      maximumFractionDigits: 0,
    }).format(n);
  } catch {
    return `${n} ETB`;
  }
}

export function formatEtbRange(min?: number | null, max?: number | null): string {
  if (min == null && max == null) return "—";
  const a = formatEtb(min);
  const b = formatEtb(max);
  if (min != null && max != null) return `${a} – ${b}`;
  return a !== "—" ? a : b;
}
