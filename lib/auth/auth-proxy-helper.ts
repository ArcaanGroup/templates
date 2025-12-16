import { NextRequest, NextResponse } from "next/server";
import { ROUTE_PERMISSIONS } from "./route-protection-table";
import { serverAction } from "../axios";
import { StandardResponseUser, User } from "../gen/schema";

export async function authProxyHandler(request: NextRequest) {
  const requestPathname = request.nextUrl.pathname;
  const [_route, requiredPermissions] =
    Object.entries(ROUTE_PERMISSIONS).find(
      ([route, _routePermissions]) => route === requestPathname,
    ) ?? [];
  const isRouteProtected = Boolean(requiredPermissions);
  if (isRouteProtected) {
    let user;
    try {
      const res = await serverAction<StandardResponseUser>(
        "GET",
        "/api/auth/me",
      );
      if (!res.data?.success) {
        throw new Error("Not authenticated");
      }
      user = res.data.payload as User;
    } catch {
      // Not authenticated users for a protected route
      // get redirected to home
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
