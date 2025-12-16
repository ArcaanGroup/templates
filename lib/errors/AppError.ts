import axios from "axios";

/**
 * Application Error Types
 *
 * Defines standardized error codes and types for the application
 */

export enum AppErrorCode {
  // Authentication errors
  AUTH_LOGIN_FAILED = "AUTH_LOGIN_FAILED",
  AUTH_REFRESH_FAILED = "AUTH_REFRESH_FAILED",
  AUTH_FORBIDDEN = "AUTH_FORBIDDEN",
  AUTH_UNAUTHORIZED = "AUTH_UNAUTHORIZED",
  AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED",

  // Network errors
  NETWORK_ERROR = "NETWORK_ERROR",
  REQUEST_TIMEOUT = "REQUEST_TIMEOUT",
  REQUEST_ERROR = "REQUEST_ERROR",

  // Generic errors
  UNEXPECTED_ERROR = "UNEXPECTED_ERROR",
  VALIDATION_ERROR = "VALIDATION_ERROR",

  // API specific errors
  API_ERROR = "API_ERROR",
  RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED",
}

export type AppError = {
  code: AppErrorCode;
  message: string;
  details?: unknown;
  originalError?: unknown;
};

/**
 * Creates a standardized application error
 */
export function createAppError(
  code: AppErrorCode,
  message: string,
  details?: unknown,
  originalError?: unknown,
): AppError {
  return {
    code,
    message,
    details,
    originalError,
  };
}

/**
 * Type guard to check if an error is an AppError
 */
export function isAppError(error: unknown): error is AppError {
  return (
    typeof error === "object" &&
    error !== null &&
    "code" in error &&
    Object.values(AppErrorCode).includes((error as AppError).code)
  );
}

/**
 * Type guard to check if an error is an Axios error
 * Returns the error cast to an Axios-like object with known properties
 * This is a wrapper around axios.isAxiosError for type safety
 */
export function isAxiosError(error: unknown): error is AxiosErrorLike {
  return axios.isAxiosError(error);
}

interface AxiosErrorLike {
  isAxiosError: boolean;
  response?: {
    status?: number;
    data?: unknown;
    headers?: unknown;
  };
  config?: unknown;
  code?: string;
  timeout?: number;
  message?: string;
}

/**
 * Transforms various error types to AppError
 */
export function transformError(
  error: unknown,
  defaultCode: AppErrorCode = AppErrorCode.UNEXPECTED_ERROR,
): AppError {
  if (isAppError(error)) {
    return error;
  }

  // Axios error handling
  if (isAxiosError(error)) {
    if (error?.response?.status === 401) {
      return createAppError(
        AppErrorCode.AUTH_UNAUTHORIZED,
        "Unauthorized access",
        error?.response?.data,
      );
    } else if (error?.response?.status === 403) {
      return createAppError(
        AppErrorCode.AUTH_FORBIDDEN,
        "Access forbidden",
        error?.response?.data,
      );
    } else if (error?.response?.status === 429) {
      return createAppError(
        AppErrorCode.RATE_LIMIT_EXCEEDED,
        "Rate limit exceeded",
        error?.response?.headers,
      );
    } else if (error?.code === "ECONNABORTED" || error?.timeout) {
      return createAppError(AppErrorCode.REQUEST_TIMEOUT, "Request timeout");
    } else {
      // Safely extract message from response data
      const message =
        typeof error?.response?.data === "object" &&
        error?.response?.data !== null &&
        "message" in error?.response?.data
          ? (error?.response?.data as { message?: string }).message
          : undefined;

      return createAppError(
        AppErrorCode.API_ERROR,
        message || error?.message || "API request failed",
        error?.response?.data,
      );
    }
  }

  // Standard Error
  if (error instanceof Error) {
    return createAppError(defaultCode, error.message, undefined, error);
  }

  // Fallback
  return createAppError(defaultCode, "An unexpected error occurred", {
    originalError: error,
  });
}
