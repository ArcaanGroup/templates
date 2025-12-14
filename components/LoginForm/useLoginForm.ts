import { useLoginApiAuthLoginPost } from "@/gen/hook";
import { UserLogin } from "@/gen/schema";

interface LoginFormInterface {
  onSubmit: (input: UserLogin) => Promise<void>;
  isPending: boolean;
  isError: boolean;
}

export default function useLoginForm(): LoginFormInterface {
  const { mutate, isPending, isError } = useLoginApiAuthLoginPost();

  async function onSubmit(input: UserLogin) {
    try {
      mutate({ data: input });
    } catch (error) {
      console.error(error);
    }
  }

  return {
    onSubmit,
    isPending,
    isError,
  };
}
