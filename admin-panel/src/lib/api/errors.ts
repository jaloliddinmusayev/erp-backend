import { AxiosError } from "axios";
import { toast } from "sonner";
import { tGlobal } from "@/lib/i18n/translate";

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function extractDetail(data: unknown): string {
  if (!data || typeof data !== "object") return tGlobal("errors.unknown");
  const d = data as Record<string, unknown>;
  if (typeof d.detail === "string") return d.detail;
  if (Array.isArray(d.detail)) {
    return d.detail
      .map((item) => {
        if (typeof item === "object" && item && "msg" in item) {
          return String((item as { msg: string }).msg);
        }
        return String(item);
      })
      .join("; ");
  }
  return tGlobal("errors.requestFailed");
}

export function parseAxiosError(error: unknown): ApiError {
  if (error instanceof ApiError) return error;
  if (error instanceof AxiosError) {
    const status = error.response?.status ?? 500;
    const detail = extractDetail(error.response?.data);
    return new ApiError(status, detail);
  }
  if (error instanceof Error) return new ApiError(500, error.message);
  return new ApiError(500, tGlobal("errors.unknown"));
}

export function handleMutationError(error: unknown, fallback?: string): void {
  const apiError = parseAxiosError(error);
  toast.error(fallback ?? apiError.detail);
}

/** TanStack Query `onError` handler */
export function onMutationError(error: unknown): void {
  handleMutationError(error);
}

export function handleQueryError(error: unknown): void {
  const apiError = parseAxiosError(error);
  if (apiError.status !== 401) {
    toast.error(apiError.detail);
  }
}
