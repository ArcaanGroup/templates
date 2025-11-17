import { redirect } from 'next/navigation';
import { routing } from '@/i18n/routing';

/**
 * Root Page
 * Redirects to the default locale
 * With localePrefix: 'as-needed', the default locale is accessible at /
 * but we still need this page for Next.js routing
 */
export default function RootPage() {
  // This should be handled by middleware, but we include it as a fallback
  redirect(`/${routing.defaultLocale}`);
}

