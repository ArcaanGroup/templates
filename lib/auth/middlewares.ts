import { ROUTE_PERMISSIONS } from "@/auth/route-protection-table";
import { serverAction } from "@/axios";
import { transformError } from "@/errors/AppError";
import {
  StandardResponseUser,
  User
} from "@/gen/schema";
import { NextRequest, NextResponse } from "next/server";

export async function authMiddleware(request: NextRequest): Promise<{
  redirect?: NextResponse;
  user?: User;
}> {
  const user = await authenticate(request);
  const requestPathname = request.nextUrl.pathname;
  const [, requiredPermissions] =
    Object.entries(ROUTE_PERMISSIONS).find(
      ([route]) => route === requestPathname,
    ) ?? [];
  const isRouteProtected = Boolean(requiredPermissions);
  if (isRouteProtected) {
    if (user === null) {
      // Redirect to home if user is not authenticated
      return {
        redirect: NextResponse.redirect(new URL("/", request.url)),
      };
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
          return { redirect: NextResponse.redirect(new URL("/", request.url)) };
        }
      } else {
        // Redirect to home if user has no permissions
        return { redirect: NextResponse.redirect(new URL("/", request.url)) };
      }
    }
  }
  return { user: user ?? undefined }; // Return undefined if no redirect is needed
}

export async function authenticate(requset: NextRequest): Promise<User | null> {
  try {
    const res = await serverAction<StandardResponseUser>("GET", "/api/auth/me");
    if (!res.data?.payload) {
      throw new Error("Not authenticated.");
    }
    return res.data?.payload as User;
  } catch (error) {
    // Log the error but don't throw - just return null for unauthenticated
    const appError = transformError(error);
    console.error("Authentication check failed:", appError);
    return null;
  }
}
