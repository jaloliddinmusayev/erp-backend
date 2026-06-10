import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from "axios";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

let getToken: (() => string | null) | null = null;
let onUnauthorized: (() => void) | null = null;

export function registerAuthHandlers(handlers: {
  getToken: () => string | null;
  onUnauthorized: () => void;
}) {
  getToken = handlers.getToken;
  onUnauthorized = handlers.onUnauthorized;
}

function attachAuth(config: InternalAxiosRequestConfig) {
  const token = getToken?.();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30_000,
});

apiClient.interceptors.request.use(attachAuth);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      onUnauthorized?.();
    }
    return Promise.reject(error);
  },
);

export interface ListParams {
  skip?: number;
  limit?: number;
  [key: string]: string | number | boolean | undefined;
}

export function buildListParams(
  page: number,
  pageSize: number,
  filters?: Record<string, string | number | boolean | undefined>,
): ListParams {
  return {
    skip: (page - 1) * pageSize,
    limit: pageSize,
    ...filters,
  };
}
