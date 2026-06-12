"use client";

import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { PageHeader } from "@/components/shared/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import { onMutationError } from "@/lib/api/errors";
import { createClient, getClient, updateClient } from "@/lib/api/modules/clients";
import { useT } from "@/lib/i18n";
import { ClientForm } from "./client-form";
import {
  clientDefaultValues,
  clientFormToPayload,
  clientToFormValues,
  type ClientFormValues,
} from "./schemas";

interface ClientFormPageProps {
  mode: "create" | "edit";
  id?: number;
}

export function ClientFormPage({ mode, id }: ClientFormPageProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const t = useT();

  const { data, isLoading } = useQuery({
    queryKey: ["clients", id],
    queryFn: () => getClient(id!),
    enabled: mode === "edit" && !!id,
  });

  const mutation = useMutation({
    mutationFn: (values: ClientFormValues) => {
      const body = clientFormToPayload(values);
      return mode === "create"
        ? createClient(body)
        : updateClient(id!, body);
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      toast.success(
        mode === "create"
          ? t("toast.created", { name: t("modules.client") })
          : t("toast.updated", { name: t("modules.client") }),
      );
      router.push(`/clients/${result.id}`);
    },
    onError: onMutationError,
  });

  if (mode === "edit" && (isLoading || !data)) {
    return <Skeleton className="h-96 w-full" />;
  }

  const title =
    mode === "create"
      ? t("common.newTitle", { name: t("modules.client") })
      : t("common.editTitle", { name: t("modules.client") });

  return (
    <div className="space-y-6">
      <PageHeader
        title={title}
        breadcrumbs={[
          { label: t("modules.clients"), href: "/clients" },
          ...(mode === "edit" && id ? [{ label: `#${id}` }] : []),
        ]}
      />
      <ClientForm
        defaultValues={mode === "edit" && data ? clientToFormValues(data) : clientDefaultValues}
        onSubmit={async (values) => {
          await mutation.mutateAsync(values);
        }}
        loading={mutation.isPending}
        submitLabel={mode === "create" ? t("common.create") : t("common.save")}
      />
    </div>
  );
}
