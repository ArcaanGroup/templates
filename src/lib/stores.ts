import { writable } from "svelte/store";

// Create a writable store for the current locale
const createLocaleStore = () => {
  const { subscribe, set, update } = writable("fa"); // Default to Persian

  return {
    subscribe,
    set,
    update,
    // Toggle between English and Persian
    toggle: () => update((current) => (current === "en" ? "fa" : "en")),
    // Set to English
    setEnglish: () => set("en"),
    // Set to Persian
    setPersian: () => set("fa"),
  };
};

// Create a writable store for the current theme
const createThemeStore = () => {
  // Check for user preference first, then system preference, then default to light
  // Only access localStorage and window APIs in the browser environment
  let initialTheme = "light"; // default to light theme

  if (typeof window !== "undefined") {
    const storedTheme = localStorage.getItem("theme");
    const systemPrefersDark = window.matchMedia(
      "(prefers-color-scheme: dark)",
    ).matches;
    initialTheme = storedTheme || (systemPrefersDark ? "dark" : "light");
  }

  const { subscribe, set, update } = writable(initialTheme);

  return {
    subscribe,
    set,
    update,
    // Toggle between light and dark themes
    toggle: () => update((current) => (current === "light" ? "dark" : "light")),
    // Set to light theme
    setLight: () => set("light"),
    // Set to dark theme
    setDark: () => set("dark"),
  };
};

export const localeStore = createLocaleStore();
export const themeStore = createThemeStore();
