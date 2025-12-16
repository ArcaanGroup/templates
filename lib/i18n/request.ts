import { getRequestConfig } from "next-intl/server";
import { routing } from "./routing";
import { getLocaleCodes } from "./config";

/**
 * i18n Request Configuration
 * This is used by next-intl to configure the request context
 */
export default getRequestConfig(async ({ requestLocale }) => {
  // This typically corresponds to the `[locale]` segment
  let locale = await requestLocale;

  // Ensure that a valid locale is used
  const validLocales = getLocaleCodes();
  if (!locale || !validLocales.includes(locale)) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`@/../messages/${locale}.json`)).default,
  };
});
