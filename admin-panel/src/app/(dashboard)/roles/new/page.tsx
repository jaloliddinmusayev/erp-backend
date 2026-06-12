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
import { useT } from "@/lib/i18n";

const schema = z.object({
  name: z.string().min(1, "validation.nameRequired"),
  code: z.string().min(1, "validation.codeRequired"),
  description: z.string().optional(),
});

export default function NewRolePage() {
  const router = useRouter();
  const t = useT();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createRole,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles"] });
      toast.success(t("toast.roleCreated"));
      router.push("/roles");
    },
    onError: onMutationError,
  });

  return (
    <PermissionGuard permission="roles:write">
      <div className="space-y-6">
        <PageHeader
          title={t("common.newTitle", { name: t("modules.role") })}
          breadcrumbs={[{ label: t("modules.roles"), href: "/roles" }, { label: t("common.new") }]}
        />
        <Card><CardContent className="pt-6">
          <ResourceForm
            schema={schema}
            fields={[
              { name: "code", label: "fields.code", required: true },
              { name: "name", label: "fields.name", required: true },
              { name: "description", label: "fields.description", type: "textarea" },
            ]}
            loading={mutation.isPending}
            onSubmit={(v) => mutation.mutate(v as never)}
          />
        </CardContent></Card>
      </div>
    </PermissionGuard>
  );
}
