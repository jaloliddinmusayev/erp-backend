"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { listUsers } from "@/lib/api/modules/users";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/shared/status-badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useT } from "@/lib/i18n";

export default function UserViewPage({ params }: { params: Promise<{ id: string }> }) {
  const t = useT();
  const { id } = use(params);
  const { data, isLoading } = useQuery({
    queryKey: ["users", id],
    queryFn: async () => {
      const list = await listUsers({ skip: 0, limit: 500 });
      return list.find((u) => u.id === Number(id));
    },
  });

  if (isLoading) return <Skeleton className="h-48" />;
  if (!data) return <p>{t("common.notFound")}</p>;

  return (
    <div className="space-y-6">
      <PageHeader title={data.full_name} breadcrumbs={[{ label: t("modules.users"), href: "/users" }, { label: data.email }]} />
      <Card><CardContent className="grid gap-4 pt-6 sm:grid-cols-2">
        <div><p className="text-sm text-muted-foreground">{t("fields.email")}</p><p>{data.email}</p></div>
        <div><p className="text-sm text-muted-foreground">{t("fields.roleId")}</p><p>{data.role_id}</p></div>
        <div><p className="text-sm text-muted-foreground">{t("fields.status")}</p><StatusBadge status={data.is_active ? "active" : "inactive"} /></div>
      </CardContent></Card>
    </div>
  );
}
