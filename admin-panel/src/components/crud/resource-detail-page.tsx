"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Pencil } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/shared/page-header";
import { PermissionGuard } from "@/components/crud/permission-guard";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { handleQueryError } from "@/lib/api/errors";
import { formatDateTime } from "@/lib/utils";
import { useT } from "@/lib/i18n";
import type { ResourceConfig } from "@/config/resources/types";

interface DetailField {
  label: string;
  value: React.ReactNode;
}

interface ResourceDetailPageProps<T> {
  config: ResourceConfig<T>;
  id: number;
  getFields: (item: T) => DetailField[];
  actions?: React.ReactNode;
}

export function ResourceDetailPage<T>({
  config,
  id,
  getFields,
  actions,
}: ResourceDetailPageProps<T>) {
  const t = useT();
  const { data, isLoading, isError, error } = useQuery({
    queryKey: [config.key, id],
    queryFn: () => config.get!(id),
    enabled: !!config.get,
  });

  if (isError) handleQueryError(error);

  if (isLoading || !data) {
    return <Skeleton className="h-96 w-full" />;
  }

  const item = data as T & { created_at?: string; updated_at?: string };
  const fields = getFields(data);

  return (
    <div className="space-y-6">
      <PageHeader
        title={`${t(config.labelSingularKey)} #${id}`}
        breadcrumbs={[
          { label: t(config.labelKey), href: config.basePath },
          { label: `#${id}` },
        ]}
        action={
          <div className="flex gap-2">
            {actions}
            {config.supportsEdit !== false && config.update && (
              <PermissionGuard permission={config.permissions.write}>
                <Button variant="outline" asChild>
                  <Link href={`${config.basePath}/${id}/edit`}>
                    <Pencil className="mr-2 h-4 w-4" />
                    {t("common.edit")}
                  </Link>
                </Button>
              </PermissionGuard>
            )}
          </div>
        }
      />

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t("common.details")}</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-4 sm:grid-cols-2">
            {fields.map((f) => (
              <div key={f.label}>
                <dt className="text-sm text-muted-foreground">{t(f.label)}</dt>
                <dd className="mt-1 font-medium">{f.value}</dd>
              </div>
            ))}
            {item.created_at && (
              <div>
                <dt className="text-sm text-muted-foreground">{t("common.createdAt")}</dt>
                <dd className="mt-1 font-medium">
                  {formatDateTime(item.created_at)}
                </dd>
              </div>
            )}
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}
