import { defineRouting } from 'next-intl/routing';
import { createNavigation } from 'next-intl/navigation';
import { getLocaleCodes, defaultLocale } from './config';

/**
 * Routing configuration for next-intl
 * This defines how locales are handled in URLs
 */
export const routing = defineRouting({
  // A list of all locales that are supported
  locales: getLocaleCodes(),

  // Used when no locale matches
  defaultLocale: defaultLocale,

  // The prefix is used to determine if a locale should be part of the URL
  // 'as-needed' means the default locale won't have a prefix in the URL
  // 'always' means all locales will have a prefix
  localePrefix: 'as-needed',
});

/**
 * Navigation helpers that are aware of the locale
 * Use these instead of Next.js's default navigation
 */
export const { Link, redirect, usePathname, useRouter } =
  createNavigation(routing);

