import { apiClient, type ListParams } from "../client";
import type { Invoice } from "@/types/api";

export async function listInvoices(params: ListParams) {
  const { data } = await apiClient.get<Invoice[]>("/invoices/", { params });
  return data;
}

export async function getInvoice(id: number) {
  const { data } = await apiClient.get<Invoice>(`/invoices/${id}`);
  return data;
}

export async function createInvoice(body: Record<string, unknown>) {
  const { data } = await apiClient.post<Invoice>("/invoices/", body);
  return data;
}

export async function updateInvoice(id: number, body: Record<string, unknown>) {
  const { data } = await apiClient.put<Invoice>(`/invoices/${id}`, body);
  return data;
}

export async function issueInvoice(id: number) {
  const { data } = await apiClient.patch<Invoice>(`/invoices/${id}/issue`);
  return data;
}

export async function cancelInvoice(id: number) {
  const { data } = await apiClient.patch<Invoice>(`/invoices/${id}/cancel`);
  return data;
}

export async function deactivateInvoice(id: number) {
  const { data } = await apiClient.patch<Invoice>(`/invoices/${id}/deactivate`);
  return data;
}
