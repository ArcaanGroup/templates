"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

/**
 * Theme Toggle Component
 *
 * A button component that allows users to toggle between light, dark, and system themes.
 * Features:
 * - Shows current theme with icon
 * - Cycles through: system → light → dark → system
 * - Prevents hydration mismatch
 * - Accessible with ARIA labels
 * - Smooth transitions
 */
export default function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  // Don't render until mounted to prevent hydration issues
  if (!mounted) {
    return (
      <button
        type="button"
        className="flex h-9 w-9 items-center justify-center rounded-lg border border-gray-300 bg-white text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
        aria-label="Toggle theme"
        disabled
      >
        <div className="h-4 w-4" />
      </button>
    );
  }

  const cycleTheme = () => {
    // Define the theme cycling sequence
    const themeOrder = ["system", "light", "dark"];
    const currentIndex = themeOrder.indexOf(theme || "system");
    const nextIndex = (currentIndex + 1) % themeOrder.length;
    setTheme(themeOrder[nextIndex]);
  };

  // Determine which icon to show based on resolved theme (actual theme being used)
  const getIcon = () => {
    const currentTheme = resolvedTheme || theme;

    if (currentTheme === "dark") {
      // Moon icon for dark mode
      return (
        <svg
          className="h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
          />
        </svg>
      );
    } else if (currentTheme === "light") {
      // Sun icon for light mode
      return (
        <svg
          className="h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
      );
    } else {
      // System/monitor icon for system theme
      return (
        <svg
          className="h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
          />
        </svg>
      );
    }
  };

  const getAriaLabel = () => {
    const currentTheme = resolvedTheme || theme;
    if (theme === "system") {
      return `System theme (${currentTheme}) - Click to switch to light`;
    } else if (theme === "light") {
      return "Light theme - Click to switch to dark";
    } else {
      return "Dark theme - Click to switch to system";
    }
  };

  return (
    <button
      type="button"
      onClick={cycleTheme}
      className="flex h-9 w-9 items-center justify-center rounded-lg border border-gray-300 bg-white text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
      aria-label={getAriaLabel()}
      title={getAriaLabel()}
    >
      {getIcon()}
    </button>
  );
}
