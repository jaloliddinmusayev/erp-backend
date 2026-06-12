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
import type { MessageKey } from "@/lib/i18n/translate";

export interface NavItem {
  titleKey: MessageKey;
  href: string;
  icon: LucideIcon;
  permissions: Permission[];
  adminOnly?: boolean;
}

export const mainNavigation: NavItem[] = [
  {
    titleKey: "nav.dashboard",
    href: "/",
    icon: LayoutDashboard,
    permissions: ["dashboard:view"],
  },
  {
    titleKey: "nav.products",
    href: "/products",
    icon: Package,
    permissions: ["products:read"],
  },
  {
    titleKey: "nav.clients",
    href: "/clients",
    icon: Users,
    permissions: ["clients:read"],
  },
  {
    titleKey: "nav.salesOrders",
    href: "/sales-orders",
    icon: ShoppingCart,
    permissions: ["sales_orders:read"],
  },
  {
    titleKey: "nav.warehouses",
    href: "/warehouses",
    icon: Warehouse,
    permissions: ["warehouses:read"],
  },
  {
    titleKey: "nav.payments",
    href: "/payments",
    icon: CreditCard,
    permissions: ["payments:read"],
  },
  {
    titleKey: "nav.invoices",
    href: "/invoices",
    icon: FileText,
    permissions: ["invoices:read"],
  },
  {
    titleKey: "nav.receivables",
    href: "/receivables",
    icon: PieChart,
    permissions: ["receivables:read"],
  },
  {
    titleKey: "nav.users",
    href: "/users",
    icon: UserCog,
    permissions: ["users:read"],
    adminOnly: true,
  },
  {
    titleKey: "nav.roles",
    href: "/roles",
    icon: Shield,
    permissions: ["roles:read"],
    adminOnly: true,
  },
  {
    titleKey: "nav.settings",
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
