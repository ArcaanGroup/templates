import { Link } from "@/i18n/routing";
import { useTranslations } from "next-intl";

export default function Page() {
  const t = useTranslations("ProtectedPage");

  return (
    <div className="max-w-90 mx-auto h-screen flex flex-col justify-center items-center gap-4">
      <h1>
        <strong>{t("title")}</strong>
      </h1>
      <Link
        href="/"
        className="w-full bg-emerald-800 hover:bg-emerald-600 text-white text-center font-medium py-2 px-4 rounded-md transition duration-200"
      >
        {t("backLink")}
      </Link>
    </div>
  );
}
