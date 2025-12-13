"use client";

import { useCallback, useRef } from "react";
import { axiosInstance, ApiError } from "./instance";
import type { AxiosRequestConfig, CancelTokenSource } from "axios";

interface UseApiOptions {
  onSuccess?: (data: unknown) => void;
  onError?: (error: ApiError) => void;
  onFinally?: () => void;
}

export const useApi = () => {
  const cancelTokenSource = useRef<CancelTokenSource | null>(null);

  const request = useCallback(
    async <T = unknown>(
      config: AxiosRequestConfig,
      options?: UseApiOptions,
    ): Promise<T> => {
      // Create cancel token for this request
      const source = axiosInstance.CancelToken.source();
      cancelTokenSource.current = source;

      try {
        const response = await axiosInstance({
          ...config,
          cancelToken: source.token,
        });

        options?.onSuccess?.(response.data);
        return response.data;
      } catch (error) {
        if (!axiosInstance.isCancel(error)) {
          options?.onError?.(error as ApiError);
        }
        throw error;
      } finally {
        options?.onFinally?.();
      }
    },
    [],
  );

  const cancelRequest = useCallback(() => {
    if (cancelTokenSource.current) {
      cancelTokenSource.current.cancel("Request cancelled by user");
      cancelTokenSource.current = null;
    }
  }, []);

  // Convenience methods
  const get = useCallback(
    <T = unknown>(
      url: string,
      config?: AxiosRequestConfig,
      options?: UseApiOptions,
    ) => request<T>({ ...config, url, method: "GET" }, options),
    [request],
  );

  const post = useCallback(
    <T = unknown>(
      url: string,
      data?: unknown,
      config?: AxiosRequestConfig,
      options?: UseApiOptions,
    ) => request<T>({ ...config, url, method: "POST", data }, options),
    [request],
  );

  const put = useCallback(
    <T = unknown>(
      url: string,
      data?: unknown,
      config?: AxiosRequestConfig,
      options?: UseApiOptions,
    ) => request<T>({ ...config, url, method: "PUT", data }, options),
    [request],
  );

  const patch = useCallback(
    <T = unknown>(
      url: string,
      data?: unknown,
      config?: AxiosRequestConfig,
      options?: UseApiOptions,
    ) => request<T>({ ...config, url, method: "PATCH", data }, options),
    [request],
  );

  const del = useCallback(
    <T = unknown>(
      url: string,
      config?: AxiosRequestConfig,
      options?: UseApiOptions,
    ) => request<T>({ ...config, url, method: "DELETE" }, options),
    [request],
  );

  return {
    request,
    get,
    post,
    put,
    patch,
    delete: del,
    cancelRequest,
  };
};
