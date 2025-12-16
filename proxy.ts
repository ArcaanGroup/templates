import createMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";
import { NextRequest, NextResponse } from "next/server";
import {
  authenticationMiddleware,
  authorizationMiddleware,
} from "./lib/auth/middlewares";

// Define types for extensible middleware functionality
export type ProxyHandler = (
  request: NextRequest,
) => Promise<NextResponse | undefined>;

/**
 * Main middleware function that combines
 * authentication, authorization and internationalization.
 */
export default async function proxy(request: NextRequest) {
  const user = await authenticationMiddleware();
  const redirectTo = await authorizationMiddleware(request, user);
  if (redirectTo) return redirectTo;

  const i18nMiddleware = createMiddleware(routing);
  const i18nResponse = i18nMiddleware(request);

  return i18nResponse;
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
