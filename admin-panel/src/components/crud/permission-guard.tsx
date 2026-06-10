"use client";

import { hasPermission, type Permission } from "@/config/permissions";
import { useAuthStore } from "@/stores/auth-store";

interface PermissionGuardProps {
  permission: Permission;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function PermissionGuard({
  permission,
  children,
  fallback = null,
}: PermissionGuardProps) {
  const roleCode = useAuthStore((s) => s.user?.role.code ?? "");
  if (!hasPermission(roleCode, permission)) return <>{fallback}</>;
  return <>{children}</>;
}
