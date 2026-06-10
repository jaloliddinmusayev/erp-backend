import { apiClient, type ListParams } from "../client";
import type { Role } from "@/types/api";

export async function listRoles(params: ListParams) {
  const { data } = await apiClient.get<Role[]>("/roles/", { params });
  return data;
}

export async function createRole(body: Record<string, unknown>) {
  const { data } = await apiClient.post<Role>("/roles/", body);
  return data;
}
