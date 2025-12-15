"use client";

import React, { PropsWithChildren } from "react";
import { AuthProvider } from "@/lib/contexts/auth-context";
import { User } from "@/lib/gen/schema";

interface Props extends PropsWithChildren {
  user?: User;
}

export default function AuthProviderWrapper({ children, user }: Props) {
  return <AuthProvider initialUser={user}>{children}</AuthProvider>;
}
