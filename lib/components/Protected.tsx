import { useAuth } from "@/contexts/auth-context";
import { PropsWithChildren, memo } from "react";
import ErrorBoundary from "./ErrorBoundary";

type Props = {
  reverse?: boolean;
  requiredPermissions?: string[];
} & PropsWithChildren;

const Protected = memo(function ProtectedComponent({
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

  return <ErrorBoundary>{children}</ErrorBoundary>;
});

export default Protected;
