import { PropsWithChildren } from "react";
import { Geist, Geist_Mono } from "next/font/google";
import { defaultLocale, getLocaleConfig } from "@/i18n/config";
import { headers } from "next/headers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default async function RootLayout({ children }: PropsWithChildren) {
  const locale = (await headers()).get("x-locale") || defaultLocale;
  const localeConfig = getLocaleConfig(locale);

  return (
    <html lang={locale} dir={localeConfig.dir} suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
