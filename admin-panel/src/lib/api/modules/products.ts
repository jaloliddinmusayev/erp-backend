import { apiClient, buildListParams, type ListParams } from "../client";
import type { Product } from "@/types/api";

export async function listProducts(params: ListParams) {
  const { data } = await apiClient.get<Product[]>("/products/", { params });
  return data;
}

export async function getProduct(id: number) {
  const { data } = await apiClient.get<Product>(`/products/${id}`);
  return data;
}

export async function createProduct(body: Record<string, unknown>) {
  const { data } = await apiClient.post<Product>("/products/", body);
  return data;
}

export async function updateProduct(id: number, body: Record<string, unknown>) {
  const { data } = await apiClient.put<Product>(`/products/${id}`, body);
  return data;
}

export async function deactivateProduct(id: number) {
  const { data } = await apiClient.patch<Product>(`/products/${id}/deactivate`);
  return data;
}

export { buildListParams };
