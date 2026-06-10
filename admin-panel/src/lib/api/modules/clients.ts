import { apiClient, type ListParams } from "../client";
import type { Client } from "@/types/api";

export async function listClients(params: ListParams) {
  const { data } = await apiClient.get<Client[]>("/clients/", { params });
  return data;
}

export async function getClient(id: number) {
  const { data } = await apiClient.get<Client>(`/clients/${id}`);
  return data;
}

export async function createClient(body: Record<string, unknown>) {
  const { data } = await apiClient.post<Client>("/clients/", body);
  return data;
}

export async function updateClient(id: number, body: Record<string, unknown>) {
  const { data } = await apiClient.put<Client>(`/clients/${id}`, body);
  return data;
}

export async function deactivateClient(id: number) {
  const { data } = await apiClient.patch<Client>(`/clients/${id}/deactivate`);
  return data;
}
