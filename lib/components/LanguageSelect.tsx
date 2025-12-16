"use client";

import { useState, useRef, useEffect } from "react";
import { useLocale } from "next-intl";
import { useRouter, usePathname } from "@/i18n/routing";
import { getAvailableLocales, isRTL } from "@/i18n";
import { getLocaleConfig } from "@/i18n/config";

/**
 * Language Select Dropdown Component
 *
 * A dropdown component for switching between available locales.
 * Features:
 * - Shows current locale with flag and name
 * - Dropdown menu with all available locales
 * - RTL/LTR support
 * - Click outside to close
 * - Keyboard navigation support
 */
export default function LanguageSelect() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const locales = getAvailableLocales();
  const currentLocale = getLocaleConfig(locale);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const isRTLMode = isRTL(locale);

  const switchLocale = (newLocale: string) => {
    router.replace(pathname, { locale: newLocale });
    setIsOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  // Close dropdown on Escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen]);

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Dropdown Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
        aria-label="Select language"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <span className="text-lg">{currentLocale.flag}</span>
        <span className="hidden sm:inline">{currentLocale.name}</span>
        <span className="sm:hidden">{currentLocale.code.toUpperCase()}</span>
        <svg
          className={`h-4 w-4 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          className={`absolute z-50 mt-2 w-48 rounded-lg border border-gray-200 bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none dark:border-gray-700 dark:bg-gray-800 ${
            isRTLMode ? "left-0 origin-top-left" : "right-0 origin-top-right"
          }`}
        >
          <div className="py-1" role="menu" aria-orientation="vertical">
            {locales.map((loc) => {
              const isActive = locale === loc.code;
              return (
                <button
                  key={loc.code}
                  type="button"
                  onClick={() => switchLocale(loc.code)}
                  className={`flex w-full items-center gap-3 px-4 py-2 text-sm transition-colors ${
                    isActive
                      ? "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400"
                      : "text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-700"
                  }`}
                  role="menuitem"
                  aria-current={isActive ? "true" : undefined}
                >
                  <span className="text-lg">{loc.flag}</span>
                  <span
                    className={`flex-1 ${
                      isRTLMode ? "text-left" : "text-right"
                    }`}
                  >
                    {loc.name}
                  </span>
                  {isActive && (
                    <svg
                      className="h-4 w-4 text-blue-600 dark:text-blue-400"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                      aria-hidden="true"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
