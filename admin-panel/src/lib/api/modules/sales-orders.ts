import { apiClient, type ListParams } from "../client";
import type { SalesOrder } from "@/types/api";

export async function listSalesOrders(params: ListParams) {
  const { data } = await apiClient.get<SalesOrder[]>("/sales-orders/", { params });
  return data;
}

export async function getSalesOrder(id: number) {
  const { data } = await apiClient.get<SalesOrder>(`/sales-orders/${id}`);
  return data;
}

export async function createSalesOrder(body: Record<string, unknown>) {
  const { data } = await apiClient.post<SalesOrder>("/sales-orders/", body);
  return data;
}

export async function updateSalesOrder(id: number, body: Record<string, unknown>) {
  const { data } = await apiClient.put<SalesOrder>(`/sales-orders/${id}`, body);
  return data;
}

export async function confirmSalesOrder(id: number) {
  const { data } = await apiClient.patch<SalesOrder>(`/sales-orders/${id}/confirm`);
  return data;
}

export async function cancelSalesOrder(id: number) {
  const { data } = await apiClient.patch<SalesOrder>(`/sales-orders/${id}/cancel`);
  return data;
}

export async function deactivateSalesOrder(id: number) {
  const { data } = await apiClient.patch<SalesOrder>(`/sales-orders/${id}/deactivate`);
  return data;
}

export async function enqueueWms(id: number) {
  const { data } = await apiClient.post(`/sales-orders/${id}/enqueue-wms`);
  return data;
}
