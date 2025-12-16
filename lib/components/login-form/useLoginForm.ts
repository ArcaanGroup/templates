import { useAuth } from "@/contexts/auth-context";
import { UserLogin } from "@/gen/schema";
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
  const { login, isPending } = useAuth();

  async function onSubmit(input: UserLogin) {
    try {
      await login(input);
      setError(null);
    } catch {
      setError(t("features.auth.login.messages.failed"));
    }
  }

  return {
    onSubmit,
    isPending,
    error,
  };
}
