'use client';

/**
 * Locale Switcher Component
 * 
 * Example component demonstrating:
 * - Client-side locale switching
 * - Using useRouter from next-intl
 * - Accessing available locales
 */

import { useLocale } from 'next-intl';
import { useRouter, usePathname } from '@/i18n/routing';
import { getAvailableLocales } from '@/lib/i18n';

export default function LocaleSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const locales = getAvailableLocales();

  const switchLocale = (newLocale: string) => {
    router.replace(pathname, { locale: newLocale });
  };

  return (
    <div className="flex gap-2">
      {locales.map((loc) => (
        <button
          key={loc.code}
          onClick={() => switchLocale(loc.code)}
          className={`px-4 py-2 rounded-md transition-colors ${
            locale === loc.code
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600'
          }`}
          aria-label={`Switch to ${loc.name}`}
        >
          {loc.flag && <span className="mr-2">{loc.flag}</span>}
          {loc.code.toUpperCase()}
        </button>
      ))}
    </div>
  );
}

