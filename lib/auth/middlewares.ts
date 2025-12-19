import { ROUTE_PERMISSIONS } from "@/auth/route-protection-table";
import { serverAction } from "@/axios";
import { AppErrorCode, transformError } from "@/errors/AppError";
import {
  StandardResponseToken,
  StandardResponseUser,
  User,
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
    if (!res.data?.success) {
      if (res.error === AppErrorCode.AUTH_UNAUTHORIZED) {
        try {
          const refreshTokenResponse =
            await serverAction<StandardResponseToken>(
              "POST",
              "/api/auth/refresh",
            );
          if (
            !refreshTokenResponse.data?.success ||
            !refreshTokenResponse.data.payload?.token
          )
            return null;

          const newAccessToken = refreshTokenResponse.data.payload.token;
          requset.headers.set("x-new-access-token", newAccessToken);
          // Get the user again
          const res = await serverAction<StandardResponseUser>(
            "GET",
            "/api/auth/me",
            undefined,
            { explicitAccessToken: newAccessToken },
          );
          return res.data?.payload as User;
        } catch {
          return null;
        }
      }
      return null;
    }
    return res.data.payload as User;
  } catch (error) {
    // Log the error but don't throw - just return null for unauthenticated
    const appError = transformError(error);
    console.error("Authentication check failed:", appError);
    return null;
  }
}
