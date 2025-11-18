import LanguageSelect from "@/components/LanguageSelect";
import ThemeToggle from "@/components/ThemeToggle";
import { getTranslations, setRequestLocale } from "next-intl/server";

/**
 * Home Page
 * This page demonstrates:
 * - Using translations with getTranslations (server-side)
 * - Locale-aware navigation with the Link component
 * - RTL/LTR support (handled automatically by the layout)
 */
export default async function Home({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  const t = await getTranslations("home");

  return (
    <div className="w-screen h-screen flex flex-col justify-center items-center gap-3">
      <h1>{t("title")}</h1>
      <div className="flex gap-2 items-center">
        <LanguageSelect />
        <ThemeToggle />
      </div>
    </div>
  );
}
