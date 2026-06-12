"use client";

import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";
import { toast } from "sonner";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { ResourceForm } from "@/components/forms/resource-form";
import { listRoles } from "@/lib/api/modules/roles";
import { createUser } from "@/lib/api/modules/users";
import { onMutationError } from "@/lib/api/errors";
import { PermissionGuard } from "@/components/crud/permission-guard";
import { useT } from "@/lib/i18n";

const schema = z.object({
  full_name: z.string().min(1, "validation.nameRequired"),
  email: z.string().email("validation.emailInvalid"),
  password: z.string().min(6, "validation.passwordMin"),
  role_id: z.number().min(1, "validation.roleRequired"),
});

export default function NewUserPage() {
  const router = useRouter();
  const t = useT();
  const queryClient = useQueryClient();
  const { data: roles = [] } = useQuery({
    queryKey: ["roles"],
    queryFn: () => listRoles({ skip: 0, limit: 100 }),
  });

  const mutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success(t("toast.userCreated"));
      router.push("/users");
    },
    onError: onMutationError,
  });

  return (
    <PermissionGuard permission="users:write">
      <div className="space-y-6">
        <PageHeader
          title={t("common.newTitle", { name: t("modules.user") })}
          breadcrumbs={[{ label: t("modules.users"), href: "/users" }, { label: t("common.new") }]}
        />
        <Card><CardContent className="pt-6">
          <ResourceForm
            schema={schema}
            fields={[
              { name: "full_name", label: "fields.fullName", required: true },
              { name: "email", label: "fields.email", type: "email", required: true },
              { name: "password", label: "fields.password", type: "text", required: true },
              { name: "role_id", label: "fields.role", type: "select", required: true, options: roles.map((r) => ({ label: r.name, value: String(r.id) })) },
            ]}
            loading={mutation.isPending}
            onSubmit={(v) => mutation.mutate(v as never)}
          />
        </CardContent></Card>
      </div>
    </PermissionGuard>
  );
}
