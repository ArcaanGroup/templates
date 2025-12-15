import { UserLogin } from "@/lib/gen/schema";
import { useAuthStore } from "@/lib/stores/auth";
import { useTranslations } from "next-intl";
import { useState } from "react";

interface LoginFormInterface {
  onSubmit: (input: UserLogin) => Promise<void>;
  isPending: boolean;
  error: string | null;
}

export default function useLoginForm(): LoginFormInterface {
  const t = useTranslations();
  const [error, setError] = useState<string | null>(null);
  const { login, isPending } = useAuthStore();

  async function onSubmit(input: UserLogin) {
    try {
      await login(input);
      setError(null);
    } catch (err) {
      setError(t("features.auth.login.messages.failed"));
      throw err;
    }
  }

  return {
    onSubmit,
    isPending,
    error,
  };
}
