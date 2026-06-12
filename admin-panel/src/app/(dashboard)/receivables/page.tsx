"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getAging, getAgingInvoices } from "@/lib/api/modules/receivables";
import { formatMoney, formatDate } from "@/lib/utils";
import { handleQueryError } from "@/lib/api/errors";
import { useT, type MessageKey } from "@/lib/i18n";
import type { AgingBucketSummary } from "@/types/api";

const AGING_BUCKETS: {
  key: keyof Omit<AgingBucketSummary, "total_outstanding">;
  labelKey: MessageKey;
}[] = [
  { key: "current", labelKey: "receivables.bucketCurrent" },
  { key: "days_1_30", labelKey: "receivables.bucket1_30" },
  { key: "days_31_60", labelKey: "receivables.bucket31_60" },
  { key: "days_61_90", labelKey: "receivables.bucket61_90" },
  { key: "days_90_plus", labelKey: "receivables.bucket90Plus" },
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
        <Skeleton className="h-64" />
      ) : (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">
                {t("receivables.totalOutstanding", { date: formatDate(data?.as_of_date) })}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {formatMoney(summary?.total_outstanding ?? 0)}
              </p>
              {!hasOutstanding && (
                <p className="mt-2 text-sm text-muted-foreground">
                  {t("receivables.noOutstanding")}
                </p>
              )}
            </CardContent>
          </Card>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {AGING_BUCKETS.map(({ key, labelKey }) => (
              <Card key={key}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {t(labelKey)}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">
                    {formatMoney(summary?.[key] ?? 0)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {t("receivables.invoiceCount", { count: bucketCounts[key] ?? 0 })}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
