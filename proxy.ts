import createI18nMiddleware from "next-intl/middleware";
import { routing } from "./lib/i18n/routing";
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
  let user;

  try {
    user = await authenticationMiddleware();
  } catch (error) {
    // If authentication fails due to an error, treat as unauthenticated
    console.error("Authentication middleware error:", error);
    user = null;
  }

  // Pass user data via request headers for the layout to use
  const requestHeaders = new Headers(request.headers);

  if (user) {
    // Store user in headers (for server components)
    requestHeaders.set("x-user-data", JSON.stringify(user));

    const redirectTo = await authorizationMiddleware(request, user);
    if (redirectTo) return redirectTo;

    const i18nMiddleware = createI18nMiddleware(routing);
    const i18nResponse = i18nMiddleware(request);

    // Merge i18n response with our user headers
    i18nResponse.headers.set("x-user-data", requestHeaders.get("x-user-data")!);
    return i18nResponse;
  } else {
    // No user - still pass null explicitly
    requestHeaders.set("x-user-data", "null");

    const redirectTo = await authorizationMiddleware(request, null);
    if (redirectTo) return redirectTo;

    const i18nMiddleware = createI18nMiddleware(routing);
    return i18nMiddleware(request);
  }
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
