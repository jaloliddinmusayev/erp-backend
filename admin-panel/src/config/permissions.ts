export type Permission =
  | "dashboard:view"
  | "products:read"
  | "products:write"
  | "clients:read"
  | "clients:write"
  | "sales_orders:read"
  | "sales_orders:write"
  | "warehouses:read"
  | "warehouses:write"
  | "payments:read"
  | "payments:write"
  | "invoices:read"
  | "invoices:write"
  | "receivables:read"
  | "users:read"
  | "users:write"
  | "roles:read"
  | "roles:write"
  | "settings:view";

export const ALL_PERMISSIONS: Permission[] = [
  "dashboard:view",
  "products:read",
  "products:write",
  "clients:read",
  "clients:write",
  "sales_orders:read",
  "sales_orders:write",
  "warehouses:read",
  "warehouses:write",
  "payments:read",
  "payments:write",
  "invoices:read",
  "invoices:write",
  "receivables:read",
  "users:read",
  "users:write",
  "roles:read",
  "roles:write",
  "settings:view",
];

/** Non-admin roles can be extended here. */
export const ROLE_PERMISSIONS: Record<string, Permission[]> = {
  admin: ALL_PERMISSIONS,
  manager: [
    "dashboard:view",
    "products:read",
    "products:write",
    "clients:read",
    "clients:write",
    "sales_orders:read",
    "sales_orders:write",
    "warehouses:read",
    "payments:read",
    "payments:write",
    "invoices:read",
    "invoices:write",
    "receivables:read",
    "settings:view",
  ],
  viewer: [
    "dashboard:view",
    "products:read",
    "clients:read",
    "sales_orders:read",
    "warehouses:read",
    "payments:read",
    "invoices:read",
    "receivables:read",
    "settings:view",
  ],
};

export function getPermissionsForRole(roleCode: string): Permission[] {
  const code = roleCode.toLowerCase();
  return ROLE_PERMISSIONS[code] ?? ROLE_PERMISSIONS.viewer;
}

export function hasPermission(
  roleCode: string,
  permission: Permission,
): boolean {
  return getPermissionsForRole(roleCode).includes(permission);
}

export function hasAnyPermission(
  roleCode: string,
  permissions: Permission[],
): boolean {
  const userPerms = getPermissionsForRole(roleCode);
  return permissions.some((p) => userPerms.includes(p));
}
