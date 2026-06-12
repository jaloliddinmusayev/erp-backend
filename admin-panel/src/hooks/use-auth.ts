"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import * as authApi from "@/lib/api/modules/auth";
import { parseAxiosError } from "@/lib/api/errors";
import { useAuthStore } from "@/stores/auth-store";
import { tGlobal } from "@/lib/i18n";

export function useAuth() {
  const router = useRouter();
  const { token, user, isAuthenticated, setAuth, logout } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: async ({
      email,
      password,
    }: {
      email: string;
      password: string;
    }) => {
      const tokenRes = await authApi.login(email, password);
      useAuthStore.setState({
        token: tokenRes.access_token,
        isAuthenticated: true,
      });
      const me = await authApi.getMe();
      return { token: tokenRes.access_token, user: me };
    },
    onSuccess: ({ token: t, user: u }) => {
      setAuth(t, u);
      toast.success(tGlobal("auth.welcome", { name: u.full_name }));
      router.replace("/");
    },
    onError: (err) => {
      const apiError = parseAxiosError(err);
      toast.error(apiError.detail || tGlobal("auth.loginError"));
    },
  });

  const handleLogout = useCallback(() => {
    logout();
    router.replace("/login");
  }, [logout, router]);

  return {
    token,
    user,
    isAuthenticated,
    login: loginMutation.mutate,
    loginLoading: loginMutation.isPending,
    logout: handleLogout,
  };
}
