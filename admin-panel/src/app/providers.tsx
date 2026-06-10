"use client";

import { useEffect, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { Toaster } from "sonner";
import { registerAuthHandlers } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth-store";

function AuthBridge() {
  const token = useAuthStore((s) => s.token);
  const logout = useAuthStore((s) => s.logout);

  useEffect(() => {
    registerAuthHandlers({
      getToken: () => useAuthStore.getState().token,
      onUnauthorized: () => {
        logout();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
      },
    });
  }, [logout]);

  useEffect(() => {
    registerAuthHandlers({
      getToken: () => token,
      onUnauthorized: () => {
        logout();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
      },
    });
  }, [token, logout]);

  return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <AuthBridge />
        {children}
        <Toaster richColors position="top-right" closeButton />
      </ThemeProvider>
    </QueryClientProvider>
  );
}
