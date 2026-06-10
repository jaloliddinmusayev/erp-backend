import { apiClient, type ListParams } from "../client";
import type { Warehouse } from "@/types/api";

export async function listWarehouses(params: ListParams) {
  const { data } = await apiClient.get<Warehouse[]>("/warehouses/", { params });
  return data;
}

export async function createWarehouse(body: Record<string, unknown>) {
  const { data } = await apiClient.post<Warehouse>("/warehouses/", body);
  return data;
}
