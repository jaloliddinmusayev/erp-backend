"use client";

import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getAging } from "@/lib/api/modules/receivables";
import { formatMoney, formatDate } from "@/lib/utils";
import { handleQueryError } from "@/lib/api/errors";

export default function ReceivablesPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["receivables", "aging"],
    queryFn: () => getAging(),
  });

  if (isError) handleQueryError(error);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Receivables"
        description="Qarzdorlik yoshi (aging) — ochiq fakturalar bo'yicha"
      />

      {isLoading ? (
        <Skeleton className="h-64" />
      ) : (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">
                Umumiy qarz — {formatDate(data?.as_of_date)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{formatMoney(data?.total_outstanding)}</p>
            </CardContent>
          </Card>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data?.buckets.map((bucket) => (
              <Card key={bucket.bucket}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {bucket.label}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{formatMoney(bucket.total_outstanding)}</p>
                  <p className="text-xs text-muted-foreground">{bucket.invoice_count} ta faktura</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
