"use client";

import LanguageSelect from "@/components/LanguageSelect";
import ThemeToggle from "@/components/ThemeToggle";
import { useTranslations } from "next-intl";
import LoginForm from "../login-form/LoginForm";
import { useAuthStore } from "@/lib/stores/auth";

export default function HomePage() {
  const t = useTranslations("home");
  const { user, logout } = useAuthStore();

  return (
    <div className="w-screen h-screen flex flex-col justify-center items-center gap-3">
      <h1>{t("title")}</h1>
      <div className="flex gap-2 items-center">
        <LanguageSelect />
        <ThemeToggle />
      </div>
      {Boolean(user) ? <button onClick={logout}>Logout</button> : <LoginForm />}
    </div>
  );
}
