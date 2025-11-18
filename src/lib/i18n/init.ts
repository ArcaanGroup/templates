import { browser } from '$app/environment';
import { locale, waitLocale, addMessages } from 'svelte-i18n';

// Import translation files
import en from './locales/en.json';
import fa from './locales/fa.json';

// Initialize i18n
export async function initI18n(userLocale: string) {
	// Add translation messages
	addMessages('en', en);
	addMessages('fa', fa);

	// Set the locale
	locale.set(userLocale);

	// Wait for locale to be loaded before continuing
	if (browser) {
		await waitLocale();
	}
}

// Export utility functions
export { locale, t } from 'svelte-i18n';
