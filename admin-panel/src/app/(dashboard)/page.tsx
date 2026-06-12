"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Package,
  Users,
  ShoppingCart,
  Clock,
  FileText,
  CreditCard,
} from "lucide-react";
import { KpiCard } from "@/components/shared/kpi-card";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchDashboardStats } from "@/lib/api/modules/dashboard";
import { formatMoney } from "@/lib/utils";
import { handleQueryError } from "@/lib/api/errors";
import { useAuthStore } from "@/stores/auth-store";
import { useT } from "@/lib/i18n";

export default function DashboardPage() {
  const t = useT();
  const user = useAuthStore((s) => s.user);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: fetchDashboardStats,
  });

  if (isError) handleQueryError(error);

  return (
    <div className="space-y-8">
      <PageHeader
        title={t("nav.dashboard")}
        description={t("dashboard.welcome", { name: user?.full_name ?? "" })}
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <KpiCard
          title={t("dashboard.totalProducts")}
          value={data?.totalProducts ?? 0}
          icon={Package}
          loading={isLoading}
        />
        <KpiCard
          title={t("dashboard.totalClients")}
          value={data?.totalClients ?? 0}
          icon={Users}
          loading={isLoading}
        />
        <KpiCard
          title={t("dashboard.totalSalesOrders")}
          value={data?.totalSalesOrders ?? 0}
          icon={ShoppingCart}
          loading={isLoading}
        />
        <KpiCard
          title={t("dashboard.openOrders")}
          value={data?.openOrders ?? 0}
          icon={Clock}
          loading={isLoading}
          description={t("dashboard.openOrdersDesc")}
        />
        <KpiCard
          title={t("dashboard.invoicesOutstanding")}
          value={formatMoney(data?.invoicesOutstanding ?? 0)}
          icon={FileText}
          loading={isLoading}
        />
        <KpiCard
          title={t("dashboard.paymentsReceived")}
          value={formatMoney(data?.paymentsReceived ?? 0)}
          icon={CreditCard}
          loading={isLoading}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t("dashboard.tenantInfo")}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-2 text-sm sm:grid-cols-2">
          <p>
            <span className="text-muted-foreground">{t("dashboard.user")}:</span>{" "}
            {user?.full_name}
          </p>
          <p>
            <span className="text-muted-foreground">{t("fields.role")}:</span> {user?.role.name}
          </p>
          <p>
            <span className="text-muted-foreground">{t("dashboard.companyId")}:</span>{" "}
            {user?.company_id}
          </p>
          <p>
            <span className="text-muted-foreground">{t("fields.email")}:</span> {user?.email}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
