import { sequence } from "@sveltejs/kit/hooks";
import { locale } from "svelte-i18n";
import { initI18n } from "$lib/i18n/init";

/** @type {import('@sveltejs/kit').Handle} */
async function initialization({ event, resolve }) {
  // Determine the locale from the request headers or default to Persian
  const acceptLanguage = event.request.headers.get("accept-language");
  let detectedLocale = "fa"; // Default locale

  if (acceptLanguage) {
    // Extract the primary language from Accept-Language header
    const primaryLang = acceptLanguage.split(",")[0].substring(0, 2);
    detectedLocale = ["en", "fa"].includes(primaryLang) ? primaryLang : "fa";
  }

  // Initialize the locale for this request
  locale.set(detectedLocale);

  // Initialize i18n system with the detected locale
  await initI18n(detectedLocale);

  return resolve(event);
}

export const handle = sequence(initialization);
