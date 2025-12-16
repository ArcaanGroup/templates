"use client";

import LanguageSelect from "@/components/LanguageSelect";
import ThemeToggle from "@/components/ThemeToggle";
import { useTranslations } from "next-intl";
import LoginForm from "@/components/login-form/LoginForm";
import { useAuth } from "@/contexts/auth-context";
import UserProfile from "@/components/UserProfile";
import Protected from "@/components/Protected";

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
