import { useAuth } from "@/contexts/auth-context";
import {
  AppErrorCode,
  isAppError,
  isAxiosError,
  transformError,
} from "@/errors/AppError";
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
    } catch (err: unknown) {
      const appError = transformError(err, AppErrorCode.AUTH_LOGIN_FAILED);

      // Handle different types of errors appropriately
      if (isAppError(err) && err.code === AppErrorCode.AUTH_FORBIDDEN) {
        setError(err.message || t("features.auth.login.messages.failed"));
      } else if (isAxiosError(err) && err?.response?.data) {
        // Safely extract message from response data
        const responseData = err.response.data;
        if (
          typeof responseData === "object" &&
          responseData !== null &&
          "message" in responseData
        ) {
          setError(
            (responseData as { message?: string }).message ||
              t("features.auth.login.messages.failed"),
          );
        } else {
          setError(t("features.auth.login.messages.failed"));
        }
      } else {
        setError(t("features.auth.login.messages.failed"));
      }
      throw appError;
    }
  }

  return {
    onSubmit,
    isPending,
    error,
  };
}
