"use client";

import { hasPermission, type Permission } from "@/config/permissions";
import { useAuthStore } from "@/stores/auth-store";

export function usePermissions() {
  const roleCode = useAuthStore((s) => s.user?.role.code ?? "viewer");
  const isAdmin = roleCode.toLowerCase() === "admin";

  return {
    roleCode,
    isAdmin,
    can: (permission: Permission) => hasPermission(roleCode, permission),
  };
}
