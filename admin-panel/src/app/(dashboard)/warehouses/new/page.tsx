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

const schema = z.object({
  name: z.string().min(1),
  code: z.string().min(1),
  branch_id: z.number().min(1),
  address: z.string().optional(),
});

export default function NewWarehousePage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data: branches = [] } = useQuery({
    queryKey: ["branches"],
    queryFn: () => listBranches({ skip: 0, limit: 100 }),
  });

  const mutation = useMutation({
    mutationFn: createWarehouse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["warehouses"] });
      toast.success("Ombor yaratildi");
      router.push("/warehouses");
    },
    onError: onMutationError,
  });

  return (
    <div className="space-y-6">
      <PageHeader title="Yangi Warehouse" breadcrumbs={[{ label: "Warehouses", href: "/warehouses" }, { label: "Yangi" }]} />
      <Card><CardContent className="pt-6">
        <ResourceForm
          schema={schema}
          fields={[
            { name: "code", label: "Kod", required: true },
            { name: "name", label: "Nom", required: true },
            {
              name: "branch_id",
              label: "Filial",
              type: "select",
              required: true,
              options: branches.map((b) => ({ label: b.name, value: String(b.id) })),
            },
            { name: "address", label: "Manzil", type: "textarea" },
          ]}
          loading={mutation.isPending}
          onSubmit={(v) => mutation.mutate(v as never)}
        />
      </CardContent></Card>
    </div>
  );
}
