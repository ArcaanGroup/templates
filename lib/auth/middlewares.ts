import { NextRequest, NextResponse } from "next/server";
import { serverAction } from "../axios";
import { StandardResponseUser, User } from "../gen/schema";
import { ROUTE_PERMISSIONS } from "./route-protection-table";

export async function authenticationMiddleware(): Promise<User | null> {
  try {
    const res = await serverAction<StandardResponseUser>("GET", "/api/auth/me");
    if (!res.data?.success) {
      return null; // Not authenticated
    }
    return res.data.payload as User;
  } catch (error) {
    // Log the error but don't throw - just return null for unauthenticated
    console.error("Authentication check failed:", error);
    return null;
  }
}

export async function authorizationMiddleware(
  request: NextRequest,
  user: User | null,
) {
  const requestPathname = request.nextUrl.pathname;
  const [, requiredPermissions] =
    Object.entries(ROUTE_PERMISSIONS).find(
      ([route]) => route === requestPathname,
    ) ?? [];
  const isRouteProtected = Boolean(requiredPermissions);
  if (isRouteProtected) {
    if (user === null) {
      // Redirect to home if user is not authenticated
      return NextResponse.redirect(new URL("/", request.url));
    }
    if (requiredPermissions) {
      const userPermissions = user.roles
        ?.map((role) => role.permission_ids)
        .flat()
        .filter(Boolean);
      const hasUserPermissions =
        Boolean(userPermissions) && Boolean(userPermissions?.length);
      if (hasUserPermissions) {
        if (
          !requiredPermissions.every((requiredPerm) =>
            userPermissions?.includes(requiredPerm),
          )
        ) {
          // Redirect to home if user doesn't have required permissions
          return NextResponse.redirect(new URL("/", request.url));
        }
      } else {
        // Redirect to home if user has no permissions
        return NextResponse.redirect(new URL("/", request.url));
      }
    }
  }
  return undefined; // Return undefined if no redirect is needed
}
