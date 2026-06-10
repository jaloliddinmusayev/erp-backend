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

const schema = z.object({
  full_name: z.string().min(1),
  email: z.string().email(),
  password: z.string().min(6),
  role_id: z.number().min(1),
});

export default function NewUserPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data: roles = [] } = useQuery({
    queryKey: ["roles"],
    queryFn: () => listRoles({ skip: 0, limit: 100 }),
  });

  const mutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success("Foydalanuvchi yaratildi");
      router.push("/users");
    },
    onError: onMutationError,
  });

  return (
    <PermissionGuard permission="users:write">
      <div className="space-y-6">
        <PageHeader title="Yangi User" breadcrumbs={[{ label: "Users", href: "/users" }, { label: "Yangi" }]} />
        <Card><CardContent className="pt-6">
          <ResourceForm
            schema={schema}
            fields={[
              { name: "full_name", label: "To'liq ism", required: true },
              { name: "email", label: "Email", type: "email", required: true },
              { name: "password", label: "Parol", type: "text", required: true },
              { name: "role_id", label: "Rol", type: "select", required: true, options: roles.map((r) => ({ label: r.name, value: String(r.id) })) },
            ]}
            loading={mutation.isPending}
            onSubmit={(v) => mutation.mutate(v as never)}
          />
        </CardContent></Card>
      </div>
    </PermissionGuard>
  );
}
