/**
 * i18n Utility Functions
 *
 * Helper functions for working with locales and translations
 */

import { getLocaleConfig, isValidLocale, type Locale } from "@/i18n/config";
import { routing } from "@/i18n/routing";

/**
 * Get the current locale from the URL or default locale
 */
export function getCurrentLocale(pathname: string): string {
  const segments = pathname.split("/").filter(Boolean);
  const firstSegment = segments[0];

  if (firstSegment && isValidLocale(firstSegment)) {
    return firstSegment;
  }

  return routing.defaultLocale;
}

/**
 * Get locale configuration
 */
export function getLocale(locale: string): Locale {
  return getLocaleConfig(locale);
}

/**
 * Check if locale is RTL
 */
export function isRTL(locale: string): boolean {
  return getLocaleConfig(locale).dir === "rtl";
}

/**
 * Get all available locales
 */
export function getAvailableLocales(): Locale[] {
  return routing.locales.map((code) => getLocaleConfig(code));
}

/**
 * Get locale name by code
 */
export function getLocaleName(locale: string): string {
  return getLocaleConfig(locale).name;
}
