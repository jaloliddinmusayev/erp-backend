import { apiClient, type ListParams } from "../client";
import type { Branch, Category, Unit } from "@/types/api";

export async function listCategories(params: ListParams) {
  const { data } = await apiClient.get<Category[]>("/categories/", { params });
  return data;
}

export async function listUnits(params: ListParams) {
  const { data } = await apiClient.get<Unit[]>("/units/", { params });
  return data;
}

export async function listBranches(params: ListParams) {
  const { data } = await apiClient.get<Branch[]>("/branches/", { params });
  return data;
}
