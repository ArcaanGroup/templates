"use server";

import { revalidatePath } from "next/cache";
import { cookies, headers } from "next/headers";
import { axiosInstance } from "./instance";
import { transformError } from "@/errors/AppError";

export async function serverAction<T = unknown>(
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE",
  endpoint: string,
  data?: unknown,
  options?: {
    tags?: string[];
    paths?: string[];
    cache?: "force-cache" | "no-store";
  },
): Promise<{ data?: T; error?: string }> {
  try {
    // Get request headers for SSR
    const headersList = await headers();
    const cookieStore = await cookies();

    const response = await axiosInstance({
      method,
      url: endpoint,
      data,
      headers: {
        cookie: cookieStore.toString(),
        "user-agent": headersList.get("user-agent") || "",
        "x-forwarded-for": headersList.get("x-forwarded-for") || "",
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
  } catch (error) {
    console.error("Server Action Error:", error);

    // Transform the error to a user-friendly message
    const appError = transformError(error);

    // Return user-friendly error
    return {
      error: appError.message || "An unexpected error occurred",
    };
  }
}
