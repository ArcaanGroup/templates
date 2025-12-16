import { useAuth } from "@/contexts/auth-context";
import { PropsWithChildren } from "react";

type Props = {
  reverse?: boolean;
  requiredPermissions?: string[];
} & PropsWithChildren;

export default function Protected({
  children,
  reverse,
  requiredPermissions,
}: Props) {
  const { isAuthenticated, checkUserPermissions } = useAuth();

  if (reverse) {
    if (isAuthenticated()) {
      return <></>;
    }
  } else {
    if (!isAuthenticated()) {
      return <></>;
    } else if (requiredPermissions) {
      if (!checkUserPermissions(requiredPermissions)) {
        return <></>;
      }
    }
  }

  return children;
}
