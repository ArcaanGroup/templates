import createMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";
import { NextRequest, NextResponse } from "next/server";
import { authProxyHandler } from "./lib/auth/auth-proxy-helper";

// Define types for extensible middleware functionality
export type ProxyHandler = (
  request: NextRequest,
) => Promise<NextResponse | undefined>;

/**
 * Main middleware function that combines internationalization with extensible handlers
 */
export default async function proxy(request: NextRequest) {
  const redirectTo = await authProxyHandler(request);
  if (redirectTo) return redirectTo;
  // Continue with the internationalization middleware
  return createMiddleware(routing)(request);
}

/**
 * Matcher configuration
 * This determines which routes the middleware should run on
 * - Excludes static files, API routes, and Next.js internals
 */
export const config = {
  // Match all pathnames except for
  // - … if they start with `/api`, `/_next` or `/_vercel`
  // - … the ones containing a dot (e.g. `favicon.ico`)
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
