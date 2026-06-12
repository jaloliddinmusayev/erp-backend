import type { MessageKey } from "@/lib/i18n/translate";

export type NavGroupKey = "main" | "sales" | "finance" | "admin";

export const NAV_GROUP_ORDER: NavGroupKey[] = ["main", "sales", "finance", "admin"];

export const NAV_GROUP_LABELS: Record<NavGroupKey, MessageKey> = {
  main: "nav.groupMain",
  sales: "nav.groupSales",
  finance: "nav.groupFinance",
  admin: "nav.groupAdmin",
};

export type KpiAccent = "indigo" | "violet" | "amber" | "rose" | "emerald" | "sky";

export const KPI_ACCENT_STYLES: Record<
  KpiAccent,
  { icon: string; ring: string }
> = {
  indigo: {
    icon: "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400",
    ring: "hover:ring-indigo-500/20",
  },
  violet: {
    icon: "bg-violet-500/10 text-violet-600 dark:text-violet-400",
    ring: "hover:ring-violet-500/20",
  },
  amber: {
    icon: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
    ring: "hover:ring-amber-500/20",
  },
  rose: {
    icon: "bg-rose-500/10 text-rose-600 dark:text-rose-400",
    ring: "hover:ring-rose-500/20",
  },
  emerald: {
    icon: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
    ring: "hover:ring-emerald-500/20",
  },
  sky: {
    icon: "bg-sky-500/10 text-sky-600 dark:text-sky-400",
    ring: "hover:ring-sky-500/20",
  },
};
