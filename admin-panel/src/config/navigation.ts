import {
  LayoutDashboard,
  Package,
  Users,
  ShoppingCart,
  Warehouse,
  CreditCard,
  FileText,
  PieChart,
  UserCog,
  Shield,
  Settings,
  type LucideIcon,
} from "lucide-react";
import type { Permission } from "./permissions";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  permissions: Permission[];
  adminOnly?: boolean;
}

export const mainNavigation: NavItem[] = [
  {
    title: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
    permissions: ["dashboard:view"],
  },
  {
    title: "Products",
    href: "/products",
    icon: Package,
    permissions: ["products:read"],
  },
  {
    title: "Clients",
    href: "/clients",
    icon: Users,
    permissions: ["clients:read"],
  },
  {
    title: "Sales Orders",
    href: "/sales-orders",
    icon: ShoppingCart,
    permissions: ["sales_orders:read"],
  },
  {
    title: "Warehouses",
    href: "/warehouses",
    icon: Warehouse,
    permissions: ["warehouses:read"],
  },
  {
    title: "Payments",
    href: "/payments",
    icon: CreditCard,
    permissions: ["payments:read"],
  },
  {
    title: "Invoices",
    href: "/invoices",
    icon: FileText,
    permissions: ["invoices:read"],
  },
  {
    title: "Receivables",
    href: "/receivables",
    icon: PieChart,
    permissions: ["receivables:read"],
  },
  {
    title: "Users",
    href: "/users",
    icon: UserCog,
    permissions: ["users:read"],
    adminOnly: true,
  },
  {
    title: "Roles",
    href: "/roles",
    icon: Shield,
    permissions: ["roles:read"],
    adminOnly: true,
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
    permissions: ["settings:view"],
  },
];

export function filterNavigation(
  roleCode: string,
  hasPermissionFn: (role: string, perm: Permission) => boolean,
): NavItem[] {
  const isAdmin = roleCode.toLowerCase() === "admin";
  return mainNavigation.filter((item) => {
    if (item.adminOnly && !isAdmin) return false;
    return item.permissions.some((p) => hasPermissionFn(roleCode, p));
  });
}
