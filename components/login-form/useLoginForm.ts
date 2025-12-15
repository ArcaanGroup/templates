import { useLoginApiAuthLoginPost } from "@/lib/gen/hook";
import { UserLogin } from "@/lib/gen/schema";
import { useState } from "react";

interface LoginFormInterface {
  onSubmit: (input: UserLogin) => Promise<void>;
  isPending: boolean;
  error: string | null;
}

export default function useLoginForm(): LoginFormInterface {
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const authMutation = useLoginApiAuthLoginPost();

  async function onSubmit(input: UserLogin) {
    try {
      setIsPending(true);
      await authMutation.mutateAsync({ data: input });
    } catch (err) {
      setError("Login Failed");
      throw err;
    } finally {
      setIsPending(false);
    }
  }

  return {
    onSubmit,
    isPending,
    error,
  };
}
