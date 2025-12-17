import QueryProvider from "@/components/QueryProvider";
import { ThemeProvider } from "@/components/ThemeProvider";
import VazirFont from "@/components/VazirFont";
import { getLocaleConfig } from "@/i18n/config";
import { routing } from "@/i18n/routing";
import { AuthProvider } from "@/contexts/auth-context";
import type { Metadata, ResolvingMetadata } from "next";
import { NextIntlClientProvider } from "next-intl";
import {
  getMessages,
  getTranslations,
  setRequestLocale,
} from "next-intl/server";
import { Geist, Geist_Mono } from "next/font/google";
import { headers } from "next/headers";
import { notFound } from "next/navigation";
import "../globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

type Props = {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale });

  return {
    title: t("routes.all.meta.title"),
    description: t("routes.all.meta.description"),
  };
}

/**
 * Locale-specific Layout
 * This layout handles:
 * - Locale detection and validation
 * - RTL/LTR direction support
 * - Providing translations to child components
 */
export default async function LocaleLayout({ children, params }: Props) {
  const { locale } = await params;

  // Ensure that the incoming `locale` is valid
  if (!routing.locales.includes(locale)) {
    notFound();
  }

  // Enable static rendering
  setRequestLocale(locale);

  // Get locale configuration for RTL/LTR support
  const localeConfig = getLocaleConfig(locale);
  const messages = await getMessages();

  // Get user data from proxy headers
  const headersList = await headers();
  const userHeader = headersList.get("x-user-data");
  const user = userHeader ? JSON.parse(userHeader) : null;

  return (
    <html lang={locale} dir={localeConfig.dir} suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <AuthProvider initialUser={user}>
          <QueryProvider>
            <ThemeProvider>
              <NextIntlClientProvider messages={messages}>
                <VazirFont />
                {children}
              </NextIntlClientProvider>
            </ThemeProvider>
          </QueryProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
