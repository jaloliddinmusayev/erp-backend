"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { listWarehouses } from "@/lib/api/modules/warehouses";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function WarehouseViewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data, isLoading } = useQuery({
    queryKey: ["warehouses", "detail", id],
    queryFn: async () => {
      const list = await listWarehouses({ skip: 0, limit: 500 });
      return list.find((w) => w.id === Number(id));
    },
  });

  if (isLoading) return <Skeleton className="h-48" />;
  if (!data) return <p>Topilmadi</p>;

  return (
    <div className="space-y-6">
      <PageHeader title={data.name} breadcrumbs={[{ label: "Warehouses", href: "/warehouses" }, { label: data.code }]} />
      <Card><CardContent className="grid gap-4 pt-6 sm:grid-cols-2">
        <div><p className="text-sm text-muted-foreground">Kod</p><p className="font-medium">{data.code}</p></div>
        <div><p className="text-sm text-muted-foreground">Manzil</p><p className="font-medium">{data.address ?? "—"}</p></div>
      </CardContent></Card>
    </div>
  );
}
