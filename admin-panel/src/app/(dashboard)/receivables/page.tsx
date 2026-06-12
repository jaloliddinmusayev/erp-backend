"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { PieChart } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { KpiCard } from "@/components/shared/kpi-card";
import { Skeleton } from "@/components/ui/skeleton";
import { getAging, getAgingInvoices } from "@/lib/api/modules/receivables";
import { formatMoney, formatDate } from "@/lib/utils";
import { handleQueryError } from "@/lib/api/errors";
import { useT, type MessageKey } from "@/lib/i18n";
import type { KpiAccent } from "@/config/design";
import type { AgingBucketSummary } from "@/types/api";

const AGING_BUCKETS: {
  key: keyof Omit<AgingBucketSummary, "total_outstanding">;
  labelKey: MessageKey;
  accent: KpiAccent;
}[] = [
  { key: "current", labelKey: "receivables.bucketCurrent", accent: "emerald" },
  { key: "days_1_30", labelKey: "receivables.bucket1_30", accent: "sky" },
  { key: "days_31_60", labelKey: "receivables.bucket31_60", accent: "amber" },
  { key: "days_61_90", labelKey: "receivables.bucket61_90", accent: "rose" },
  { key: "days_90_plus", labelKey: "receivables.bucket90Plus", accent: "violet" },
];

export default function ReceivablesPage() {
  const t = useT();
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["receivables", "aging"],
    queryFn: () => getAging(),
  });

  const { data: invoices = [] } = useQuery({
    queryKey: ["receivables", "aging-invoices", data?.as_of_date],
    queryFn: () => getAgingInvoices(data?.as_of_date),
    enabled: !!data,
  });

  const bucketCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const inv of invoices) {
      counts[inv.aging_bucket] = (counts[inv.aging_bucket] ?? 0) + 1;
    }
    return counts;
  }, [invoices]);

  if (isError) handleQueryError(error);

  const summary = data?.summary;
  const hasOutstanding = summary && Number(summary.total_outstanding) > 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("nav.receivables")}
        description={t("receivables.description")}
      />

      {isLoading ? (
        <Skeleton className="h-64 rounded-2xl" />
      ) : (
        <>
          <KpiCard
            title={t("receivables.totalOutstanding", { date: formatDate(data?.as_of_date) })}
            value={formatMoney(summary?.total_outstanding ?? 0)}
            icon={PieChart}
            accent="rose"
            money
            description={!hasOutstanding ? t("receivables.noOutstanding") : undefined}
          />

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {AGING_BUCKETS.map(({ key, labelKey, accent }) => (
              <KpiCard
                key={key}
                title={t(labelKey)}
                value={formatMoney(summary?.[key] ?? 0)}
                icon={PieChart}
                accent={accent}
                money
                description={t("receivables.invoiceCount", { count: bucketCounts[key] ?? 0 })}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
