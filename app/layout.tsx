/**
 * Root Layout
 * This is the top-level layout that wraps all pages
 * The locale-specific layout is in app/[locale]/layout.tsx
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
