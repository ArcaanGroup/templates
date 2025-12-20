import createI18nMiddleware from "next-intl/middleware";
import { NextRequest } from "next/server";
import { authMiddleware } from "./lib/auth/middlewares";
import { routing } from "./lib/i18n/routing";
import { Key } from "@/utils/key.enum";

/**
 * Main middleware function that combines
 * authentication, authorization and internationalization.
 */
export default async function proxy(request: NextRequest) {
  const { redirect, user } = await authMiddleware(request);
  if (redirect) return redirect;

  const i18nMiddleware = createI18nMiddleware(routing);
  const i18nResponse = i18nMiddleware(request);

  const locale = request.nextUrl.pathname.split("/")[1];
  if (locale) {
    i18nResponse.headers.set("x-locale", locale);
  }

  if (user) {
    // Set user data as response header
    // so we can get it on the root layout (server component)
    i18nResponse.headers.set("x-user-data", JSON.stringify(user));
  }

  const newAccessToken = request.headers.get("x-new-access-token");
  if (newAccessToken) {
    i18nResponse.cookies.set(Key.AccessToken, newAccessToken);
  }

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
