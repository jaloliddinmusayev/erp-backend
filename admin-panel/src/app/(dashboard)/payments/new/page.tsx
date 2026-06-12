"use client";

import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";
import { toast } from "sonner";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { ResourceForm } from "@/components/forms/resource-form";
import { listClients } from "@/lib/api/modules/clients";
import { createPayment } from "@/lib/api/modules/payments";
import { onMutationError } from "@/lib/api/errors";
import { useT } from "@/lib/i18n";

const schema = z.object({
  client_id: z.number().min(1, "validation.clientRequired"),
  amount: z.number().positive("validation.amountPositive"),
  payment_date: z.string().min(1, "validation.dateRequired"),
  payment_method: z.enum(["cash", "bank_transfer", "card", "other"]),
  reference_number: z.string().optional(),
  notes: z.string().optional(),
});

export default function NewPaymentPage() {
  const router = useRouter();
  const t = useT();
  const queryClient = useQueryClient();
  const { data: clients = [] } = useQuery({
    queryKey: ["clients"],
    queryFn: () => listClients({ skip: 0, limit: 200, is_active: true }),
  });

  const mutation = useMutation({
    mutationFn: createPayment,
    onSuccess: (d) => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      toast.success(t("toast.paymentCreated"));
      router.push(`/payments/${d.id}`);
    },
    onError: onMutationError,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("common.newTitle", { name: t("modules.payment") })}
        breadcrumbs={[{ label: t("modules.payments"), href: "/payments" }, { label: t("common.new") }]}
      />
      <Card><CardContent className="pt-6">
        <ResourceForm
          schema={schema}
          defaultValues={{ payment_date: new Date().toISOString().slice(0, 10), payment_method: "cash" }}
          fields={[
            { name: "client_id", label: "fields.client", type: "select", required: true, options: clients.map((c) => ({ label: c.name, value: String(c.id) })) },
            { name: "amount", label: "fields.amount", type: "number", required: true },
            { name: "payment_date", label: "fields.date", type: "date", required: true },
            { name: "payment_method", label: "fields.method", type: "select", required: true, options: [
              { label: t("paymentMethod.cash"), value: "cash" }, { label: t("paymentMethod.bank_transfer"), value: "bank_transfer" },
              { label: t("paymentMethod.card"), value: "card" }, { label: t("paymentMethod.other"), value: "other" },
            ]},
            { name: "reference_number", label: "fields.reference" },
            { name: "notes", label: "fields.notes", type: "textarea" },
          ]}
          loading={mutation.isPending}
          onSubmit={(v) => mutation.mutate(v as never)}
        />
      </CardContent></Card>
    </div>
  );
}
