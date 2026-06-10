"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import * as authApi from "@/lib/api/modules/auth";
import { handleMutationError } from "@/lib/api/errors";
import { useAuthStore } from "@/stores/auth-store";

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
      toast.success(`Xush kelibsiz, ${u.full_name}!`);
      router.replace("/");
    },
    onError: (err) => handleMutationError(err, "Login xatosi"),
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
