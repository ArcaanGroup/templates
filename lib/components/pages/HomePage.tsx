"use client";

import LanguageSelect from "@/lib/components/LanguageSelect";
import ThemeToggle from "@/lib/components/ThemeToggle";
import { useTranslations } from "next-intl";
import LoginForm from "../login-form/LoginForm";
import { useAuth } from "@/lib/contexts/auth-context";
import UserProfile from "../UserProfile";
import Protected from "../Protected";

export default function HomePage() {
  const t = useTranslations("home");
  const { user } = useAuth();

  return (
    <div className="w-screen h-screen flex flex-col justify-center items-center gap-3">
      <h1>{t("title")}</h1>
      <div className="flex gap-2 items-center">
        <LanguageSelect />
        <ThemeToggle />
      </div>
      <Protected reverse>
        <LoginForm />
      </Protected>
      <Protected>
        <UserProfile user={user!} />
      </Protected>
    </div>
  );
}
