import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { MeResponse } from "@/types/api";

interface AuthState {
  token: string | null;
  user: MeResponse | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: MeResponse) => void;
  setUser: (user: MeResponse) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      setAuth: (token, user) =>
        set({ token, user, isAuthenticated: true }),
      setUser: (user) => set({ user }),
      logout: () => set({ token: null, user: null, isAuthenticated: false }),
    }),
    {
      name: "erp-auth",
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);
