"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { listRoles } from "@/lib/api/modules/roles";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useT } from "@/lib/i18n";

export default function RoleViewPage({ params }: { params: Promise<{ id: string }> }) {
  const t = useT();
  const { id } = use(params);
  const { data, isLoading } = useQuery({
    queryKey: ["roles", id],
    queryFn: async () => {
      const list = await listRoles({ skip: 0, limit: 500 });
      return list.find((r) => r.id === Number(id));
    },
  });

  if (isLoading) return <Skeleton className="h-48" />;
  if (!data) return <p>{t("common.notFound")}</p>;

  return (
    <div className="space-y-6">
      <PageHeader title={data.name} breadcrumbs={[{ label: t("modules.roles"), href: "/roles" }, { label: data.code }]} />
      <Card><CardContent className="grid gap-4 pt-6">
        <div><p className="text-sm text-muted-foreground">{t("fields.code")}</p><p className="font-medium">{data.code}</p></div>
        <div><p className="text-sm text-muted-foreground">{t("fields.description")}</p><p>{data.description ?? "—"}</p></div>
      </CardContent></Card>
    </div>
  );
}
