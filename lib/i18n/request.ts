import { getRequestConfig } from "next-intl/server";
import { routing } from "./routing";

/**
 * i18n Request Configuration
 * This is used by next-intl to configure the request context
 */
export default getRequestConfig(async ({ requestLocale }) => {
  // This typically corresponds to the `[locale]` segment
  let locale = await requestLocale;

  // Ensure that a valid locale is used
  if (!locale || !routing.locales.includes(locale as any)) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`@/../messages/${locale}.json`)).default,
  };
});
