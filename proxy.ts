import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';

/**
 * Middleware for handling locale detection and routing
 * This runs on every request and handles:
 * - Locale detection from Accept-Language header
 * - Redirecting to the appropriate locale
 * - Setting locale cookies
 */
export default createMiddleware(routing);

/**
 * Matcher configuration
 * This determines which routes the middleware should run on
 * - Excludes static files, API routes, and Next.js internals
 */
export const config = {
  // Match all pathnames except for
  // - … if they start with `/api`, `/_next` or `/_vercel`
  // - … the ones containing a dot (e.g. `favicon.ico`)
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)'],
};

