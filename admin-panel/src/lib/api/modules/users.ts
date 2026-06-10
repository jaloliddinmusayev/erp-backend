import { apiClient, type ListParams } from "../client";
import type { User } from "@/types/api";

export async function listUsers(params: ListParams) {
  const { data } = await apiClient.get<User[]>("/users/", { params });
  return data;
}

export async function createUser(body: Record<string, unknown>) {
  const { data } = await apiClient.post<User>("/users/", body);
  return data;
}
