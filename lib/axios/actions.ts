"use server";

import { AppErrorCode } from "@/errors/AppError";
import { revalidatePath } from "next/cache";
import { cookies, headers } from "next/headers";
import { axiosInstance } from "./instance";

export async function serverAction<T = unknown>(
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE",
  endpoint: string,
  data?: unknown,
  options?: {
    tags?: string[];
    paths?: string[];
    cache?: "force-cache" | "no-store";
    explicitAccessToken?: string; // Access token which passed directly
  },
): Promise<{ data?: T; error?: string }> {
  try {
    // Get request headers for SSR
    const headersList = await headers();
    const cookieStore = await cookies();
    const accessToken = cookieStore.get("access_token")?.value;
    const token = options?.explicitAccessToken || accessToken;

    const response = await axiosInstance({
      method,
      url: endpoint,
      data,
      headers: {
        cookie: cookieStore.toString(),
        "user-agent": headersList.get("user-agent") || "",
        "x-forwarded-for": headersList.get("x-forwarded-for") || "",
        Authorization: token ? `Bearer ${token}` : undefined,
      },
      ...(options?.cache && {
        next: { revalidate: options.cache === "force-cache" ? 3600 : 0 },
      }),
    });

    // Revalidate cache if needed
    // if (options?.tags?.length) {
    //   options.tags.forEach((tag) => revalidateTag(tag));
    // }

    if (options?.paths?.length) {
      options.paths.forEach((path) => revalidatePath(path));
    }

    return { data: response.data };
  } catch (error: any) {
    console.error("Server Action Error:", error);

    // Return user-friendly error
    return {
      error: error.code || AppErrorCode.NETWORK_ERROR,
    };
  }
}
