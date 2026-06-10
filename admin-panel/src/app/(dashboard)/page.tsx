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

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: fetchDashboardStats,
  });

  if (isError) handleQueryError(error);

  return (
    <div className="space-y-8">
      <PageHeader
        title="Dashboard"
        description={`Xush kelibsiz, ${user?.full_name ?? ""}. Biznes ko'rsatkichlari.`}
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <KpiCard
          title="Total Products"
          value={data?.totalProducts ?? 0}
          icon={Package}
          loading={isLoading}
        />
        <KpiCard
          title="Total Clients"
          value={data?.totalClients ?? 0}
          icon={Users}
          loading={isLoading}
        />
        <KpiCard
          title="Total Sales Orders"
          value={data?.totalSalesOrders ?? 0}
          icon={ShoppingCart}
          loading={isLoading}
        />
        <KpiCard
          title="Open Orders"
          value={data?.openOrders ?? 0}
          icon={Clock}
          loading={isLoading}
          description="Yakunlanmagan buyurtmalar"
        />
        <KpiCard
          title="Invoices Outstanding"
          value={formatMoney(data?.invoicesOutstanding ?? 0)}
          icon={FileText}
          loading={isLoading}
        />
        <KpiCard
          title="Payments Received"
          value={formatMoney(data?.paymentsReceived ?? 0)}
          icon={CreditCard}
          loading={isLoading}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Tenant ma&apos;lumoti</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-2 text-sm sm:grid-cols-2">
          <p>
            <span className="text-muted-foreground">Foydalanuvchi:</span>{" "}
            {user?.full_name}
          </p>
          <p>
            <span className="text-muted-foreground">Rol:</span> {user?.role.name}
          </p>
          <p>
            <span className="text-muted-foreground">Company ID:</span>{" "}
            {user?.company_id}
          </p>
          <p>
            <span className="text-muted-foreground">Email:</span> {user?.email}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
