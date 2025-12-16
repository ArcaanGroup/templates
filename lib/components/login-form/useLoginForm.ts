import { UserLogin } from "@/gen/schema";
import { useAuth } from "@/contexts/auth-context";
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
    } catch (err: any) {
      // Handle different types of errors appropriately
      if (err?.code === "FORBIDDEN_ERROR") {
        setError(err.message || t("features.auth.login.messages.failed"));
      } else if (err?.response?.data?.message) {
        setError(err.response.data.message);
      } else {
        setError(t("features.auth.login.messages.failed"));
      }
      throw err;
    }
  }

  return {
    onSubmit,
    isPending,
    error,
  };
}
