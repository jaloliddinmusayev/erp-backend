"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { DataTable } from "@/components/data-table/data-table";
import { PageHeader } from "@/components/shared/page-header";
import { PermissionGuard } from "@/components/crud/permission-guard";
import { Button } from "@/components/ui/button";
import { buildListParams } from "@/lib/api/client";
import { handleQueryError } from "@/lib/api/errors";
import type { ResourceConfig } from "@/config/resources/types";

const PAGE_SIZE = 20;

interface ResourceListPageProps<T> {
  config: ResourceConfig<T>;
}

export function ResourceListPage<T>({ config }: ResourceListPageProps<T>) {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");

  const { data = [], isLoading, isError, error } = useQuery({
    queryKey: [config.key, "list", page, search],
    queryFn: () =>
      config.list(
        buildListParams(page, PAGE_SIZE, {
          ...(config.searchKey && search ? { [config.searchKey]: search } : {}),
        }),
      ),
  });

  if (isError) handleQueryError(error);

  return (
    <div className="space-y-6">
      <PageHeader
        title={config.label}
        action={
          config.supportsCreate !== false && config.create ? (
            <PermissionGuard permission={config.permissions.write}>
              <Button asChild>
                <Link href={`${config.basePath}/new`}>
                  <Plus className="mr-2 h-4 w-4" />
                  Yangi {config.labelSingular}
                </Link>
              </Button>
            </PermissionGuard>
          ) : undefined
        }
      />

      <DataTable
        columns={config.columns}
        data={data}
        loading={isLoading}
        page={page}
        pageSize={PAGE_SIZE}
        hasMore={data.length === PAGE_SIZE}
        onPageChange={setPage}
        search={config.searchKey ? search : undefined}
        onSearchChange={config.searchKey ? setSearch : undefined}
        searchPlaceholder={`${config.label} qidirish...`}
      />
    </div>
  );
}
