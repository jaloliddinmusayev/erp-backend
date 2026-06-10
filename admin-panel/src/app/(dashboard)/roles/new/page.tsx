"use client";

import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";
import { toast } from "sonner";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { ResourceForm } from "@/components/forms/resource-form";
import { createRole } from "@/lib/api/modules/roles";
import { onMutationError } from "@/lib/api/errors";
import { PermissionGuard } from "@/components/crud/permission-guard";

const schema = z.object({
  name: z.string().min(1),
  code: z.string().min(1),
  description: z.string().optional(),
});

export default function NewRolePage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createRole,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles"] });
      toast.success("Rol yaratildi");
      router.push("/roles");
    },
    onError: onMutationError,
  });

  return (
    <PermissionGuard permission="roles:write">
      <div className="space-y-6">
        <PageHeader title="Yangi Role" breadcrumbs={[{ label: "Roles", href: "/roles" }, { label: "Yangi" }]} />
        <Card><CardContent className="pt-6">
          <ResourceForm
            schema={schema}
            fields={[
              { name: "code", label: "Kod", required: true },
              { name: "name", label: "Nom", required: true },
              { name: "description", label: "Tavsif", type: "textarea" },
            ]}
            loading={mutation.isPending}
            onSubmit={(v) => mutation.mutate(v as never)}
          />
        </CardContent></Card>
      </div>
    </PermissionGuard>
  );
}
