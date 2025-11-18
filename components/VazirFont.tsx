'use client';

import { useLocale } from 'next-intl';
import { useEffect } from 'react';
import { isRTL } from '@/i18n/config';

/**
 * Vazir Font Loader Component
 * 
 * Conditionally loads Vazir font for RTL locales (especially Farsi)
 * This component ensures the font is only loaded when needed
 */
export default function VazirFont() {
  const locale = useLocale();
  const shouldLoadVazir = isRTL(locale);

  useEffect(() => {
    if (shouldLoadVazir) {
      // Check if font is already loaded
      const existingLink = document.querySelector(
        'link[href*="vazirfont"]'
      );

      if (!existingLink) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href =
          'https://cdn.jsdelivr.net/gh/rastikerdar/vazirfont@v30.1.0/dist/font-face.css';
        link.crossOrigin = 'anonymous';
        document.head.appendChild(link);
      }
    }
  }, [shouldLoadVazir]);

  return null;
}

