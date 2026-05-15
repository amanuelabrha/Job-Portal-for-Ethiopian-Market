import { getTranslations } from "next-intl/server";
import { JobSearch } from "@/components/JobSearch";

export default async function JobsPage() {
  const t = await getTranslations("jobs");
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-stone-900">{t("title")}</h1>
      <JobSearch />
    </div>
  );
}
