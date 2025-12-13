import axios from "axios";
import { axiosInstance } from "./instance";
import type { AxiosRequestConfig, AxiosResponse } from "axios";

// Orval-specific types
export type OrvalFetcherConfig = {
  url: string;
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | "HEAD" | "OPTIONS";
  params?: string | number | boolean | Record<string, string>;
  data?: string | number | boolean | Record<string, string>;
  headers?: Record<string, string>;
  responseType?: "json" | "blob" | "arraybuffer" | "text" | "stream";
  baseURL?: string;
  signal?: AbortSignal;
  timeout?: number;
};

// Enhanced error type for Orval
export type OrvalError<T = unknown> = {
  status: number;
  statusText: string;
  data: T;
  config: AxiosRequestConfig;
  isAxiosError: boolean;
};

// Orval fetcher function (main export)
export const orvalFetcher = async <T = unknown>(
  config: OrvalFetcherConfig,
): Promise<T> => {
  try {
    const axiosConfig: AxiosRequestConfig = {
      url: config.url,
      method: config.method,
      params: config.params,
      data: config.data,
      headers: {
        ...config.headers,
        "Content-Type":
          config.data instanceof FormData
            ? "multipart/form-data"
            : "application/json",
      },
      responseType: config.responseType || "json",
      baseURL: config.baseURL,
      signal: config.signal,
      timeout: config.timeout,
      // Enable caching for GET requests
      ...(config.method === "GET" && {
        cache: {
          ttl: 1000 * 60 * 5, // 5 minutes cache
          ignoreCache: false,
        },
      }),
    };

    const response: AxiosResponse<T> = await axiosInstance(axiosConfig);

    // Extract data based on response type
    if (config.responseType === "blob") {
      return response.data;
    }

    // Handle paginated responses
    if (
      response.data &&
      typeof response.data === "object" &&
      "data" in response.data
    ) {
      return response.data.data as T;
    }

    return response.data;
  } catch (error) {
    // Enhanced error handling for Orval
    if (axios.isAxiosError(error)) {
      const orvalError: OrvalError = {
        status: error.response?.status || 0,
        statusText: error.response?.statusText || "Unknown Error",
        data: error.response?.data,
        config: error.config || {},
        isAxiosError: true,
      };

      // Log error in development
      if (process.env.NODE_ENV === "development") {
        console.error("Orval Fetcher Error:", {
          url: config.url,
          method: config.method,
          error: orvalError,
        });
      }

      throw orvalError;
    }

    // Non-Axios errors
    throw {
      status: 0,
      statusText: "Network Error",
      data: { message: "Network error occurred" },
      config,
      isAxiosError: false,
    };
  }
};

// Hooks-compatible fetcher (for React Query/useSWR)
export const hooksFetcher = <T = unknown>(
  url: string,
  config?: Omit<OrvalFetcherConfig, "url">,
): Promise<T> => {
  return orvalFetcher<T>({
    url,
    method: "GET",
    ...config,
  });
};
