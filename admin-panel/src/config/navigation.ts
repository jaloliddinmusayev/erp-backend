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
import type { NavGroupKey } from "./design";

export interface NavItem {
  titleKey: MessageKey;
  href: string;
  icon: LucideIcon;
  permissions: Permission[];
  groupKey: NavGroupKey;
  adminOnly?: boolean;
}

export const mainNavigation: NavItem[] = [
  {
    titleKey: "nav.dashboard",
    href: "/",
    icon: LayoutDashboard,
    permissions: ["dashboard:view"],
    groupKey: "main",
  },
  {
    titleKey: "nav.products",
    href: "/products",
    icon: Package,
    permissions: ["products:read"],
    groupKey: "sales",
  },
  {
    titleKey: "nav.clients",
    href: "/clients",
    icon: Users,
    permissions: ["clients:read"],
    groupKey: "sales",
  },
  {
    titleKey: "nav.salesOrders",
    href: "/sales-orders",
    icon: ShoppingCart,
    permissions: ["sales_orders:read"],
    groupKey: "sales",
  },
  {
    titleKey: "nav.warehouses",
    href: "/warehouses",
    icon: Warehouse,
    permissions: ["warehouses:read"],
    groupKey: "sales",
  },
  {
    titleKey: "nav.payments",
    href: "/payments",
    icon: CreditCard,
    permissions: ["payments:read"],
    groupKey: "finance",
  },
  {
    titleKey: "nav.invoices",
    href: "/invoices",
    icon: FileText,
    permissions: ["invoices:read"],
    groupKey: "finance",
  },
  {
    titleKey: "nav.receivables",
    href: "/receivables",
    icon: PieChart,
    permissions: ["receivables:read"],
    groupKey: "finance",
  },
  {
    titleKey: "nav.users",
    href: "/users",
    icon: UserCog,
    permissions: ["users:read"],
    groupKey: "admin",
    adminOnly: true,
  },
  {
    titleKey: "nav.roles",
    href: "/roles",
    icon: Shield,
    permissions: ["roles:read"],
    groupKey: "admin",
    adminOnly: true,
  },
  {
    titleKey: "nav.settings",
    href: "/settings",
    icon: Settings,
    permissions: ["settings:view"],
    groupKey: "admin",
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

export function groupNavigationItems(items: NavItem[]): Map<NavGroupKey, NavItem[]> {
  const groups = new Map<NavGroupKey, NavItem[]>();
  for (const item of items) {
    const list = groups.get(item.groupKey) ?? [];
    list.push(item);
    groups.set(item.groupKey, list);
  }
  return groups;
}
