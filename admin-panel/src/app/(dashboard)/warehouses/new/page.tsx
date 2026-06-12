"use client";

import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";
import { toast } from "sonner";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { ResourceForm } from "@/components/forms/resource-form";
import { listBranches } from "@/lib/api/modules/catalog";
import { createWarehouse } from "@/lib/api/modules/warehouses";
import { onMutationError } from "@/lib/api/errors";
import { useT } from "@/lib/i18n";

const schema = z.object({
  name: z.string().min(1, "validation.nameRequired"),
  code: z.string().min(1, "validation.codeRequired"),
  branch_id: z.number().min(1, "validation.branchRequired"),
  address: z.string().optional(),
});

export default function NewWarehousePage() {
  const router = useRouter();
  const t = useT();
  const queryClient = useQueryClient();
  const { data: branches = [] } = useQuery({
    queryKey: ["branches"],
    queryFn: () => listBranches({ skip: 0, limit: 100 }),
  });

  const mutation = useMutation({
    mutationFn: createWarehouse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["warehouses"] });
      toast.success(t("toast.warehouseCreated"));
      router.push("/warehouses");
    },
    onError: onMutationError,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("common.newTitle", { name: t("modules.warehouse") })}
        breadcrumbs={[{ label: t("modules.warehouses"), href: "/warehouses" }, { label: t("common.new") }]}
      />
      <Card><CardContent className="pt-6">
        <ResourceForm
          schema={schema}
          fields={[
            { name: "code", label: "fields.code", required: true },
            { name: "name", label: "fields.name", required: true },
            {
              name: "branch_id",
              label: "fields.branch",
              type: "select",
              required: true,
              options: branches.map((b) => ({ label: b.name, value: String(b.id) })),
            },
            { name: "address", label: "fields.address", type: "textarea" },
          ]}
          loading={mutation.isPending}
          onSubmit={(v) => mutation.mutate(v as never)}
        />
      </CardContent></Card>
    </div>
  );
}
