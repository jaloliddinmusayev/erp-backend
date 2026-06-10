import { apiClient } from "../client";
import type { MeResponse, TokenResponse } from "@/types/api";

export async function login(email: string, password: string) {
  const { data } = await apiClient.post<TokenResponse>("/auth/login", {
    email,
    password,
  });
  return data;
}

export async function getMe() {
  const { data } = await apiClient.get<MeResponse>("/auth/me");
  return data;
}
