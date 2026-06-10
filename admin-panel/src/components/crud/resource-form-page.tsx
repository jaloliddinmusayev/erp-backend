"use client";

import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/shared/page-header";
import { ResourceForm } from "@/components/forms/resource-form";
import { Skeleton } from "@/components/ui/skeleton";
import { onMutationError } from "@/lib/api/errors";
import type { FormFieldConfig } from "@/components/forms/resource-form";
import type { ResourceConfig } from "@/config/resources/types";
import type { FieldValues } from "react-hook-form";

interface ResourceFormPageProps<T> {
  config: ResourceConfig<T>;
  mode: "create" | "edit";
  id?: number;
  extraFields?: (mode: "create" | "edit") => FormFieldConfig<FieldValues>[];
}

export function ResourceFormPage<T>({
  config,
  mode,
  id,
  extraFields,
}: ResourceFormPageProps<T>) {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: [config.key, id],
    queryFn: () => config.get!(id!),
    enabled: mode === "edit" && !!id && !!config.get,
  });

  const mutation = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      mode === "create"
        ? config.create!(body)
        : config.update!(id!, body),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: [config.key] });
      toast.success(
        mode === "create"
          ? `${config.labelSingular} yaratildi`
          : `${config.labelSingular} yangilandi`,
      );
      const res = result as { id?: number };
      router.push(`${config.basePath}/${res.id ?? id}`);
    },
    onError: onMutationError,
  });

  const schema = mode === "create" ? config.createSchema : config.updateSchema;
  const baseFields =
    mode === "create" ? config.createFields : config.updateFields;
  const fields = extraFields ? extraFields(mode) : baseFields;

  if (mode === "edit" && isLoading) {
    return <Skeleton className="h-96 w-full" />;
  }

  if (!schema || !fields) return null;

  return (
    <div className="space-y-6">
      <PageHeader
        title={
          mode === "create"
            ? `Yangi ${config.labelSingular}`
            : `${config.labelSingular} tahrirlash`
        }
        breadcrumbs={[
          { label: config.label, href: config.basePath },
          {
            label: mode === "create" ? "Yangi" : `#${id}`,
          },
        ]}
      />
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Ma&apos;lumotlar</CardTitle>
        </CardHeader>
        <CardContent>
          <ResourceForm
            schema={schema as never}
            fields={fields as never}
            defaultValues={
              mode === "edit" && data
                ? (data as unknown as FieldValues)
                : undefined
            }
            loading={mutation.isPending}
            onSubmit={(values) => mutation.mutate(values as Record<string, unknown>)}
            submitLabel={mode === "create" ? "Yaratish" : "Saqlash"}
          />
        </CardContent>
      </Card>
    </div>
  );
}
