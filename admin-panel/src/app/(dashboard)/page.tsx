"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  Package,
  Users,
  ShoppingCart,
  Clock,
  FileText,
  CreditCard,
  Plus,
  UserPlus,
  Wallet,
  Sparkles,
  Building2,
  Mail,
  Shield,
} from "lucide-react";
import { KpiCard } from "@/components/shared/kpi-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchDashboardStats } from "@/lib/api/modules/dashboard";
import { formatMoney } from "@/lib/utils";
import { handleQueryError } from "@/lib/api/errors";
import { useAuthStore } from "@/stores/auth-store";
import { useT } from "@/lib/i18n";

const QUICK_ACTIONS = [
  { href: "/sales-orders/new", icon: ShoppingCart, labelKey: "dashboard.newOrder" as const, accent: "amber" as const },
  { href: "/clients/new", icon: UserPlus, labelKey: "dashboard.newClient" as const, accent: "violet" as const },
  { href: "/payments/new", icon: Wallet, labelKey: "dashboard.newPayment" as const, accent: "emerald" as const },
  { href: "/products/new", icon: Plus, labelKey: "dashboard.newProduct" as const, accent: "sky" as const },
];

export default function DashboardPage() {
  const t = useT();
  const user = useAuthStore((s) => s.user);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: fetchDashboardStats,
  });

  if (isError) handleQueryError(error);

  const today = new Intl.DateTimeFormat(undefined, {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date());

  return (
    <div className="space-y-8">
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-600 via-indigo-600 to-violet-700 p-6 text-white shadow-lg shadow-indigo-500/20 md:p-8">
        <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-white/10 blur-2xl" />
        <div className="absolute -bottom-4 right-1/4 h-24 w-24 rounded-full bg-violet-400/20 blur-xl" />
        <div className="relative flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-indigo-100">
              <Sparkles className="h-4 w-4" />
              <span className="text-sm font-medium">Triad ERP</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight md:text-3xl">
              {t("auth.welcome", { name: user?.full_name?.split(" ")[0] ?? "" })}
            </h1>
            <p className="mt-1 text-sm text-indigo-100">{t("dashboard.subtitle")}</p>
          </div>
          <p className="text-sm text-indigo-200">{today}</p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <KpiCard
          title={t("dashboard.totalProducts")}
          value={data?.totalProducts ?? 0}
          icon={Package}
          accent="sky"
          loading={isLoading}
        />
        <KpiCard
          title={t("dashboard.totalClients")}
          value={data?.totalClients ?? 0}
          icon={Users}
          accent="violet"
          loading={isLoading}
        />
        <KpiCard
          title={t("dashboard.totalSalesOrders")}
          value={data?.totalSalesOrders ?? 0}
          icon={ShoppingCart}
          accent="amber"
          loading={isLoading}
        />
        <KpiCard
          title={t("dashboard.openOrders")}
          value={data?.openOrders ?? 0}
          icon={Clock}
          accent="indigo"
          loading={isLoading}
          description={t("dashboard.openOrdersDesc")}
        />
        <KpiCard
          title={t("dashboard.invoicesOutstanding")}
          value={formatMoney(data?.invoicesOutstanding ?? 0)}
          icon={FileText}
          accent="rose"
          loading={isLoading}
          money
        />
        <KpiCard
          title={t("dashboard.paymentsReceived")}
          value={formatMoney(data?.paymentsReceived ?? 0)}
          icon={CreditCard}
          accent="emerald"
          loading={isLoading}
          money
        />
      </div>

      <div>
        <h2 className="mb-4 text-lg font-semibold tracking-tight">
          {t("dashboard.quickActions")}
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {QUICK_ACTIONS.map(({ href, icon: Icon, labelKey }) => (
            <Link
              key={href}
              href={href}
              className="group flex items-center gap-3 rounded-2xl border bg-card p-4 shadow-sm transition-all hover:border-primary/30 hover:shadow-md"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                <Icon className="h-5 w-5" />
              </div>
              <span className="text-sm font-medium">{t(labelKey)}</span>
            </Link>
          ))}
        </div>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">{t("dashboard.tenantInfo")}</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-4 sm:grid-cols-2">
            <div className="flex items-start gap-3 rounded-xl bg-muted/40 p-4">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Building2 className="h-4 w-4" />
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {t("dashboard.user")}
                </dt>
                <dd className="mt-0.5 font-medium">{user?.full_name}</dd>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-xl bg-muted/40 p-4">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-violet-500/10 text-violet-600 dark:text-violet-400">
                <Shield className="h-4 w-4" />
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {t("fields.role")}
                </dt>
                <dd className="mt-0.5 font-medium">{user?.role.name}</dd>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-xl bg-muted/40 p-4">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-sky-500/10 text-sky-600 dark:text-sky-400">
                <Building2 className="h-4 w-4" />
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {t("dashboard.companyId")}
                </dt>
                <dd className="mt-0.5 font-medium tabular-nums">{user?.company_id}</dd>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-xl bg-muted/40 p-4">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                <Mail className="h-4 w-4" />
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {t("fields.email")}
                </dt>
                <dd className="mt-0.5 font-medium">{user?.email}</dd>
              </div>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}
