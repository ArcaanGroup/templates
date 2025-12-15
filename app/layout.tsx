import AuthProviderWrapper from "@/components/providers/AuthProviderWrapper";
import { serverAction } from "@/lib/axios";
import { StandardResponseUser, User } from "@/lib/gen/schema";

/**
 * Root Layout
 * This is the top-level layout that wraps all pages
 * The locale-specific layout is in app/[locale]/layout.tsx
 */
export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  let me: User | undefined;
  try {
    const res = await serverAction<StandardResponseUser>("GET", "/api/auth/me");
    if (res.data?.success) {
      me = res.data.payload as User;
    } else {
      throw new Error("Not Authenticated");
    }
  } catch (err) {
    console.error(err);
  }

  return <AuthProviderWrapper user={me}>{children}</AuthProviderWrapper>;
}
