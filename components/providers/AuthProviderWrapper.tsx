'use client';

import React, { PropsWithChildren } from 'react';
import { AuthProvider } from '@/lib/contexts/auth-context';

export default function AuthProviderWrapper({ children }: PropsWithChildren) {
  return <AuthProvider>{children}</AuthProvider>;
}
