/**
 * i18n Configuration
 * 
 * This file contains all i18n-related configuration.
 * Modify this file to add/remove locales, change default locale, or adjust RTL settings.
 */

export type Locale = {
  code: string;
  name: string;
  dir: 'ltr' | 'rtl';
  flag?: string; // Optional: for UI display
};

/**
 * Available locales in your application
 * Add or remove locales here as needed
 */
export const locales: Locale[] = [
  {
    code: 'fa',
    name: 'فارسی',
    dir: 'rtl',
    flag: '🇮🇷',
  },
  {
    code: 'en',
    name: 'English',
    dir: 'ltr',
    flag: '🇺🇸',
  },
  // Add more locales here:
  // {
  //   code: 'ar',
  //   name: 'العربية',
  //   dir: 'rtl',
  //   flag: '🇸🇦',
  // },
];

/**
 * Default locale - used when no locale is specified in the URL
 */
export const defaultLocale: string = 'fa';

/**
 * Get locale configuration by code
 */
export function getLocaleConfig(locale: string): Locale {
  return (
    locales.find((l) => l.code === locale) ||
    locales.find((l) => l.code === defaultLocale)!
  );
}

/**
 * Check if a locale is RTL
 */
export function isRTL(locale: string): boolean {
  return getLocaleConfig(locale).dir === 'rtl';
}

/**
 * Get all locale codes
 */
export function getLocaleCodes(): string[] {
  return locales.map((locale) => locale.code);
}

/**
 * Check if a locale code is valid
 */
export function isValidLocale(locale: string): boolean {
  return locales.some((l) => l.code === locale);
}

