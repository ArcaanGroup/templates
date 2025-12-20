import { AppErrorCode, newAppError } from "@/errors/AppError";
import { StandardResponseToken } from "@/gen/schema";
import { Key } from "@/utils/key.enum";
import axios, {
  AxiosError,
  AxiosInstance,
  AxiosResponse,
  CancelTokenSource,
  InternalAxiosRequestConfig,
} from "axios";
import Cookies from "js-cookie";

// Types
export type ApiError = {
  code: AppErrorCode;
  message: string;
  details?: Record<string, unknown>;
};

export type ApiResponse<T = unknown> = {
  data: T;
  message?: string;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
    totalPages?: number;
  };
};

// Environment configuration
const isServer = typeof window === "undefined";
const baseURL =
  (isServer
    ? process.env.SERVER_SIDE_API_URL
    : process.env.NEXT_PUBLIC_API_URL) || "http://localhost:3000/api";

class AxiosClient {
  private instance: AxiosInstance;
  private isRefreshing = false;
  private refreshSubscribers: Array<{
    resolve: (value: AxiosResponse) => void;
    reject: (error: unknown) => void;
    request: InternalAxiosRequestConfig & { _retry?: boolean };
  }> = [];

  constructor() {
    this.instance = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      withCredentials: true, // For cookies/auth
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.instance.interceptors.request.use(
      async (config: InternalAxiosRequestConfig) => {
        // On server side, add server-specific headers
        if (isServer) {
          // Add SSR headers
          config.headers["x-ssr"] = "true";
          config.headers["x-request-from"] = "nextjs-server";
        } else {
          if (config.baseURL === process.env.NEXT_PUBLIC_API_URL) {
            const accessToken = Cookies.get(Key.AccessToken);
            if (accessToken)
              config.headers["Authorization"] = `Bearer ${accessToken}`;
          }
        }

        // Add request ID for tracing (using crypto.randomUUID with fallback)
        config.headers["X-Request-ID"] =
          typeof crypto !== "undefined" && crypto.randomUUID
            ? crypto.randomUUID()
            : Math.random().toString(36).substring(2, 15) +
              Math.random().toString(36).substring(2, 15);

        return config;
      },
      (error: AxiosError) => Promise.reject(error),
    );

    // Response interceptor
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        // Transform response data to match ApiResponse type
        if (response.data?.data !== undefined) {
          return {
            ...response,
            data: response.data,
          };
        }
        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & {
          _retry?: boolean;
        };

        // Handle 401 - Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (isServer) {
            return this.handleServerTokenRefresh(error, originalRequest);
          } else {
            return this.handleTokenRefresh(error, originalRequest);
          }
        }

        // Handle 403 - Forbidden
        if (error.response?.status === 403) {
          const apiError = this.transformError(error);
          apiError.code = AppErrorCode.AUTH_FORBIDDEN;
          apiError.message =
            "Access denied. You don't have permission to access this resource.";
          return Promise.reject(apiError);
        }

        // Handle 429 - Rate limiting
        if (error.response?.status === 429) {
          const retryAfterRaw = error.response.headers["retry-after"];
          // Parse the retry-after value safely, defaulting to 5 seconds
          const retryAfter = Math.min(
            60,
            Math.max(1, parseInt(retryAfterRaw as string) || 5),
          ); // Clamp between 1-60 seconds
          console.warn(`Rate limited. Retrying after ${retryAfter} seconds`);

          await new Promise((resolve) =>
            setTimeout(resolve, retryAfter * 1000),
          );

          return this.instance(originalRequest);
        }

        // Transform error to consistent format
        return Promise.reject(this.transformError(error));
      },
    );
  }

  private async handleServerTokenRefresh(
    error: AxiosError,
    originalRequest: InternalAxiosRequestConfig & { _retry?: boolean },
  ): Promise<AxiosResponse> {
    originalRequest._retry = true;

    try {
      // Extract cookies from the original request headers
      // These are passed by serverAction from Next.js cookies()
      const cookieHeader = originalRequest.headers?.["cookie"] as
        | string
        | undefined;

      if (!cookieHeader) {
        // No cookies available, cannot refresh
        throw newAppError(
          AppErrorCode.AUTH_REFRESH_FAILED,
          "No cookies available for token refresh.",
        );
      }

      // Call refresh endpoint with the same cookies from the original request
      let res;
      try {
        res = await axios.post<StandardResponseToken>(
          `${baseURL}/api/auth/refresh`,
          {},
          {
            headers: {
              cookie: cookieHeader,
            },
            withCredentials: true,
          },
        );
      } catch {}

      const accessToken = res?.data.payload?.token;
      if (!res?.data?.success || !accessToken) {
        throw newAppError(
          AppErrorCode.AUTH_REFRESH_FAILED,
          res?.data.message || "Token refresh failed. Please log in again.",
          undefined,
          res?.data?.payload,
        );
      }

      // Update the browser cookie with the new access token
      // This ensures the token is available for subsequent requests
      try {
        // Use Next.js cookies API to set the cookie in the browser
        // This only works when called from server actions/components
        const { cookies } = await import("next/headers");
        const cookieStore = await cookies();
        cookieStore.set(Key.AccessToken, accessToken, {
          httpOnly: false, // Allow client-side access (matching client behavior)
          secure: process.env.NODE_ENV === "production",
          sameSite: "strict",
          path: "/",
        });
      } catch (cookieError) {
        // If cookies() is not available in this context, log but don't fail
        // The token will still work for the current request via Authorization header
        console.warn(
          "Could not set cookie after token refresh:",
          cookieError instanceof Error ? cookieError.message : "Unknown error",
        );
      }

      // Update the Authorization header in the original request with the new token
      originalRequest.headers = originalRequest.headers || {};
      originalRequest.headers["Authorization"] = `Bearer ${accessToken}`;

      // Retry original request with the new token
      return await this.instance(originalRequest);
    } catch (refreshError) {
      // On refresh failure, throw specific error for auth handling
      throw newAppError(
        AppErrorCode.AUTH_REFRESH_FAILED,
        "Token refresh failed. Please log in again.",
        undefined,
        refreshError,
      );
    }
  }

  private async handleTokenRefresh(
    error: AxiosError,
    originalRequest: InternalAxiosRequestConfig & { _retry?: boolean },
  ): Promise<AxiosResponse> {
    originalRequest._retry = true;

    if (this.isRefreshing) {
      // If refresh is already in progress, queue this request
      return new Promise<AxiosResponse>((resolve, reject) => {
        this.refreshSubscribers.push({
          resolve,
          reject,
          request: originalRequest,
        });
      });
    }

    this.isRefreshing = true;

    try {
      // Call refresh endpoint
      // Since tokens are stored in HTTP-only cookies, no need to manually handle them
      // Just call the refresh endpoint and let the backend handle the refresh
      const res = await axios.post<StandardResponseToken>(
        `${baseURL}/api/auth/refresh`,
        {},
        { withCredentials: true },
      );
      const accessToken = res.data.payload?.token;
      if (!res.data?.success || !accessToken) {
        throw newAppError(
          AppErrorCode.AUTH_REFRESH_FAILED,
          res.data.message || "Token refresh failed. Please log in again.",
          undefined,
          res.data?.payload,
        );
      }

      // Set the new token in cookies - this ensures queued requests get the fresh token
      Cookies.set(Key.AccessToken, accessToken);

      // Clear any stale Authorization header to ensure fresh token from cookies
      if (originalRequest.headers) {
        delete originalRequest.headers["Authorization"];
      }

      // Retry original request - it will get the new token from cookies via request interceptor
      const response = await this.instance(originalRequest);

      // Execute all queued subscribers (other requests that were waiting)
      // They will retry with the new token from cookies
      this.refreshSubscribers.forEach(({ resolve, reject, request }) => {
        // Clear any stale Authorization header to ensure fresh token from cookies
        if (request.headers) {
          delete request.headers["Authorization"];
        }
        // Mark as retried to prevent infinite loops
        request._retry = true;
        // Retry the request - it will get the new token from cookies via request interceptor
        this.instance(request).then(resolve).catch(reject);
      });
      this.refreshSubscribers = [];

      return response;
    } catch (refreshError) {
      // On refresh failure, reject all queued requests
      const errorToThrow = newAppError(
        AppErrorCode.AUTH_REFRESH_FAILED,
        "Token refresh failed. Please log in again.",
        undefined,
        refreshError,
      );

      // Reject all queued subscribers
      this.refreshSubscribers.forEach(({ reject }) => {
        reject(errorToThrow);
      });
      this.refreshSubscribers = [];

      throw errorToThrow;
    } finally {
      this.isRefreshing = false;
    }
  }

  private transformError(error: AxiosError): ApiError {
    if (error.response) {
      // Server responded with error
      const data = error.response.data as Record<string, unknown>;
      const statusCode = error.response.status;

      let errorCode: AppErrorCode;
      switch (statusCode) {
        case 401:
          errorCode = AppErrorCode.AUTH_UNAUTHORIZED;
          break;
        case 403:
          errorCode = AppErrorCode.AUTH_FORBIDDEN;
          break;
        case 429:
          errorCode = AppErrorCode.RATE_LIMIT_EXCEEDED;
          break;
        default:
          errorCode = AppErrorCode.API_ERROR;
      }

      return {
        code: (data?.code as AppErrorCode) || errorCode,
        message: (data?.message as string) || error.response.statusText,
        details: data?.details as Record<string, string>,
      };
    } else if (error.request) {
      // No response received
      return {
        code: AppErrorCode.NETWORK_ERROR,
        message: "Network error. Please check your connection.",
      };
    } else {
      // Request setup error
      return {
        code: AppErrorCode.REQUEST_ERROR,
        message:
          error.message || "An error occurred while setting up the request.",
      };
    }
  }

  // Public methods
  public getInstance(): AxiosInstance {
    return this.instance;
  }

  // public setAuthToken(token: string | null): void {
  //   if (token) {
  //     this.instance.defaults.headers.common["Authorization"] =
  //       `Bearer ${token}`;
  //   } else {
  //     delete this.instance.defaults.headers.common["Authorization"];
  //   }
  // }
  public cancelRequest(source: CancelTokenSource): void {
    source.cancel("Request cancelled by user");
  }

  public createCancelToken(): CancelTokenSource {
    return axios.CancelToken.source();
  }
}

// Export singleton instance
export const axiosClient = new AxiosClient();
export const axiosInstance = axiosClient.getInstance();
