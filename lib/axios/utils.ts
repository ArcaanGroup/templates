import { AxiosRequestConfig } from "axios";
import { axiosInstance } from "./instance";

// Upload with progress
export const uploadFile = async <T = unknown>(
  url: string,
  file: File,
  onProgress?: (percentage: number) => void,
  config?: AxiosRequestConfig,
): Promise<T> => {
  const formData = new FormData();
  formData.append("file", file);

  return axiosInstance.post(url, formData, {
    ...config,
    headers: {
      ...config?.headers,
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total,
        );
        onProgress(percentCompleted);
      }
    },
  });
};

// Download file
export const downloadFile = async (
  url: string,
  filename: string,
  config?: AxiosRequestConfig,
): Promise<void> => {
  const response = await axiosInstance.get(url, {
    ...config,
    responseType: "blob",
  });

  const blob = new Blob([response.data]);
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = downloadUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);
};

// Concurrent requests with limit
export const concurrentRequests = async <T = unknown>(
  requests: Array<() => Promise<T>>,
  concurrencyLimit = 5,
): Promise<T[]> => {
  const results: T[] = [];
  const executing: Promise<void>[] = [];

  for (const request of requests) {
    const promise = request().then((result) => {
      results.push(result);
    });

    executing.push(promise);

    if (executing.length >= concurrencyLimit) {
      await Promise.race(executing);
    }
  }

  await Promise.all(executing);
  return results;
};

// Health check
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    await axiosInstance.get("/health", { timeout: 5000 });
    return true;
  } catch {
    return false;
  }
};

// Exponential backoff retry
export const retryRequest = async <T = unknown>(
  request: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 1000,
): Promise<T> => {
  let lastError: unknown;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await request();
    } catch (error) {
      lastError = error;

      if (attempt === maxRetries) break;

      // Exponential backoff with jitter
      const delay = baseDelay * Math.pow(2, attempt);
      const jitter = delay * 0.1 * Math.random();
      await new Promise((resolve) => setTimeout(resolve, delay + jitter));
    }
  }

  throw lastError;
};
