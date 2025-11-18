"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";
import { type ReactNode } from "react";

/**
 * Theme Provider Component
 *
 * Wraps the application with next-themes ThemeProvider.
 * This component:
 * - Enables system theme detection
 * - Persists theme preference in localStorage
 * - Prevents FOUC (Flash of Unstyled Content)
 * - Works with SSR/SSG
 */
export function ThemeProvider({ children, ...props }: { children: ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange={false}
      {...props}
    >
      {children}
    </NextThemesProvider>
  );
}
