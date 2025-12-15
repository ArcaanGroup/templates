import axios, {
  AxiosError,
  AxiosInstance,
  AxiosResponse,
  CancelTokenSource,
  InternalAxiosRequestConfig,
} from "axios";
import { redirect } from "next/navigation";

// Types
export type ApiError = {
  code: string;
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
  private refreshSubscribers: (() => void)[] = [];

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
        }

        // Add request ID for tracing
        config.headers["X-Request-ID"] = crypto.randomUUID();

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
        if (error.response) {
          // Server responded with error
          const duration =
            Date.now() - (error.config?.metadata?.startTime || Date.now());

          console.group("❌ Server Error Response");
          console.log("URL:", error.config?.url);
          console.log(
            "Status:",
            error.response.status,
            error.response.statusText,
          );
          console.log("Duration:", `${duration}ms`);
          console.log("Headers:", error.response.headers);
          console.log("Data:", error.response.data);
          console.log("Request Headers:", error.config?.headers);
          console.log("Request Data:", error.config?.data);
          console.groupEnd();
        } else if (error.request) {
          // Request made but no response
          console.group("🌐 Network Error (No Response)");
          console.log("URL:", error.config?.url);
          console.log("Error:", error.message);
          console.log("Request:", error.request);
          console.groupEnd();
        } else {
          // Something else
          console.error("🚨 Setup Error:", error.message);
        }

        const originalRequest = error.config as InternalAxiosRequestConfig & {
          _retry?: boolean;
        };

        // Handle 401 - Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (!isServer) {
            return this.handleTokenRefresh(error, originalRequest);
          }
        }

        // Handle 403 - Forbidden
        if (error.response?.status === 403) {
          if (!isServer) {
            // Redirect to home or show access denied
            redirect("/");
          }
        }

        // Handle 429 - Rate limiting
        if (error.response?.status === 429) {
          const retryAfter = error.response.headers["retry-after"] || 5;
          console.warn(`Rate limited. Retrying after ${retryAfter} seconds`);

          await new Promise((resolve) =>
            setTimeout(resolve, parseInt(retryAfter.toString()) * 1000),
          );

          return this.instance(originalRequest);
        }

        // Transform error to consistent format
        return Promise.reject(this.transformError(error));
      },
    );
  }

  private async handleTokenRefresh(
    error: AxiosError,
    originalRequest: InternalAxiosRequestConfig & { _retry?: boolean },
  ): Promise<AxiosResponse> {
    originalRequest._retry = true;

    if (this.isRefreshing) {
      return new Promise((resolve, reject) => {
        this.refreshSubscribers.push(() => {
          resolve(this.instance(originalRequest));
        });
      });
    }

    this.isRefreshing = true;

    try {
      // Call refresh endpoint
      // Since tokens are stored in HTTP-only cookies, no need to manually handle them
      // Just call the refresh endpoint and let the backend handle the refresh
      await axios.post(
        `${baseURL}/api/auth/refresh`,
        {},
        { withCredentials: true },
      );

      // Retry original request
      const response = await this.instance(originalRequest);

      // Execute subscribers
      this.refreshSubscribers.forEach((callback) => callback());
      this.refreshSubscribers = [];

      return response;
    } catch (refreshError) {
      // On refresh failure, remove user and redirect to login
      if (!isServer) {
        redirect("/");
      }

      throw refreshError;
    } finally {
      this.isRefreshing = false;
    }
  }

  private transformError(error: AxiosError): ApiError {
    if (error.response) {
      // Server responded with error
      const data = error.response.data as Record<string, unknown>;
      return {
        code: (data?.code as string) || `HTTP_${error.response.status}`,
        message: (data?.message as string) || error.response.statusText,
        details: data?.details as Record<string, string>,
      };
    } else if (error.request) {
      // No response received
      return {
        code: "NETWORK_ERROR",
        message: "Network error. Please check your connection.",
      };
    } else {
      // Request setup error
      return {
        code: "REQUEST_ERROR",
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
