import { NextRequest, NextResponse } from "next/server";
import { serverAction } from "../axios";
import { StandardResponseUser, User } from "../gen/schema";
import { ROUTE_PERMISSIONS } from "./route-protection-table";

export async function authenticationMiddleware(): Promise<User | null> {
  try {
    const res = await serverAction<StandardResponseUser>("GET", "/api/auth/me");
    if (!res.data?.success) {
      throw new Error("Not authenticated");
    }
    return res.data.payload as User;
  } catch {
    // Not authenticated users for a protected route
    // get redirected to home
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
          return NextResponse.redirect(new URL("/", request.url));
        }
      } else {
        return NextResponse.redirect(new URL("/", request.url));
      }
    }
  }
}
