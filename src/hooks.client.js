import { browser } from "$app/environment";
import { locale } from "svelte-i18n";
import { initI18n } from "$lib/i18n/init";

// Initialize i18n with the user's preferred language
if (browser) {
  // Get the user's language preference from localStorage or browser
  const preferredLocale =
    localStorage.getItem("locale") || navigator.language.split("-")[0] || "fa";

  // Initialize the i18n system
  initI18n(preferredLocale);

  // Set the svelte-i18n locale
  locale.set(preferredLocale);

  // Set locale in cookie for consistency with server-side
  document.cookie = `selected-locale=${preferredLocale}; Path=/; SameSite=Strict; Max-Age=${60 * 60 * 24 * 365}`;

  // Initialize theme from localStorage or system preference
  const storedTheme = localStorage.getItem("theme");
  const systemPrefersDark = window.matchMedia(
    "(prefers-color-scheme: dark)",
  ).matches;
  const initialTheme = storedTheme || (systemPrefersDark ? "dark" : "light");

  // Apply the theme to the document root
  document.documentElement.setAttribute("data-theme", initialTheme);
  document.documentElement.classList.add(initialTheme);
}

// Export default hooks
export {};
