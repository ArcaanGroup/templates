# i18n Configuration Guide

This project uses [next-intl](https://next-intl-docs.vercel.app/) for internationalization (i18n) support with full RTL/LTR locale support.

## Quick Start

### 1. Adding a New Locale

To add a new locale, edit `i18n/config.ts`:

```typescript
export const locales: Locale[] = [
  {
    code: 'en',
    name: 'English',
    dir: 'ltr',
    flag: '🇺🇸',
  },
  {
    code: 'ar',  // Add your new locale
    name: 'العربية',
    dir: 'rtl',  // Set to 'rtl' for right-to-left languages
    flag: '🇸🇦',
  },
];
```

### 2. Creating Translation Files

Create a new JSON file in the `messages/` directory for each locale:

- `messages/en.json` - English translations
- `messages/ar.json` - Arabic translations
- etc.

Example translation file structure:

```json
{
  "common": {
    "welcome": "Welcome",
    "hello": "Hello"
  },
  "home": {
    "title": "Welcome to Next.js",
    "description": "Get started by editing the page below."
  }
}
```

### 3. Changing the Default Locale

Edit `i18n/config.ts`:

```typescript
export const defaultLocale: string = 'en'; // Change to your preferred default
```

### 4. Using Translations in Components

#### Server Components

```typescript
import { getTranslations } from 'next-intl/server';
import { setRequestLocale } from 'next-intl/server';

export default async function MyPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  
  const t = await getTranslations('home');
  
  return <h1>{t('title')}</h1>;
}
```

#### Client Components

```typescript
'use client';

import { useTranslations } from 'next-intl';

export default function MyComponent() {
  const t = useTranslations('common');
  
  return <p>{t('welcome')}</p>;
}
```

### 5. Locale-Aware Navigation

Use the `Link` component from `@/i18n/routing` instead of Next.js's default `Link`:

```typescript
import { Link } from '@/i18n/routing';

export default function Navigation() {
  return (
    <Link href="/about">About</Link>
  );
}
```

### 6. RTL/LTR Support

RTL/LTR is automatically handled based on the locale configuration. The `dir` attribute is set on the `<html>` element automatically.

For RTL-specific styling, use the `[dir='rtl']` selector in your CSS:

```css
[dir='rtl'] .my-component {
  /* RTL-specific styles */
}
```

Or use Tailwind's RTL utilities if configured.

## File Structure

```
├── i18n/
│   ├── config.ts      # Locale configuration (add/remove locales here)
│   ├── request.ts     # next-intl request configuration
│   ├── routing.ts     # Routing configuration
│   └── README.md      # This file
├── messages/
│   ├── en.json        # English translations
│   └── [locale].json  # Other locale translations
├── app/
│   └── [locale]/      # Locale-specific routes
│       ├── layout.tsx # Locale layout with RTL/LTR support
│       └── page.tsx   # Pages using translations
└── middleware.ts      # Locale detection and routing
```

## API Reference

### Configuration Functions

- `getLocaleConfig(locale: string)` - Get locale configuration
- `isRTL(locale: string)` - Check if locale is RTL
- `getLocaleCodes()` - Get all locale codes
- `isValidLocale(locale: string)` - Validate locale code

### Utility Functions (lib/i18n.ts)

- `getCurrentLocale(pathname: string)` - Get locale from pathname
- `getLocale(locale: string)` - Get locale configuration
- `isRTL(locale: string)` - Check if RTL
- `getAvailableLocales()` - Get all available locales
- `getLocaleName(locale: string)` - Get locale display name

## Best Practices

1. **Always use `setRequestLocale`** in server components to enable static rendering
2. **Use the `Link` component** from `@/i18n/routing` for navigation
3. **Keep translation keys organized** by feature/page (e.g., `home.title`, `common.welcome`)
4. **Test RTL layouts** when adding RTL locales
5. **Use TypeScript** for type-safe translations (consider using `next-intl` TypeScript plugin)

## Troubleshooting

### Locale not working?

- Check that the locale is added to `i18n/config.ts`
- Ensure the translation file exists in `messages/[locale].json`
- Verify `middleware.ts` is in the root directory

### RTL not working?

- Check that `dir: 'rtl'` is set in the locale configuration
- Verify the layout is setting the `dir` attribute on the `<html>` element
- Check browser DevTools to see if `dir="rtl"` is present

### Translations not showing?

- Ensure translation keys match between the JSON file and component usage
- Check that `getTranslations` or `useTranslations` is using the correct namespace
- Verify the translation file is properly formatted JSON

