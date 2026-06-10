import { apiClient, type ListParams } from "../client";
import type { Payment } from "@/types/api";

export async function listPayments(params: ListParams) {
  const { data } = await apiClient.get<Payment[]>("/payments/", { params });
  return data;
}

export async function getPayment(id: number) {
  const { data } = await apiClient.get<Payment>(`/payments/${id}`);
  return data;
}

export async function createPayment(body: Record<string, unknown>) {
  const { data } = await apiClient.post<Payment>("/payments/", body);
  return data;
}

export async function deactivatePayment(id: number) {
  const { data } = await apiClient.patch<Payment>(`/payments/${id}/deactivate`);
  return data;
}
