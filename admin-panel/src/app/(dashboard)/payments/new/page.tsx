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

const schema = z.object({
  client_id: z.number().min(1),
  amount: z.number().positive(),
  payment_date: z.string().min(1),
  payment_method: z.enum(["cash", "bank_transfer", "card", "other"]),
  reference_number: z.string().optional(),
  notes: z.string().optional(),
});

export default function NewPaymentPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data: clients = [] } = useQuery({
    queryKey: ["clients"],
    queryFn: () => listClients({ skip: 0, limit: 200, is_active: true }),
  });

  const mutation = useMutation({
    mutationFn: createPayment,
    onSuccess: (d) => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      toast.success("To'lov yaratildi");
      router.push(`/payments/${d.id}`);
    },
    onError: onMutationError,
  });

  return (
    <div className="space-y-6">
      <PageHeader title="Yangi Payment" breadcrumbs={[{ label: "Payments", href: "/payments" }, { label: "Yangi" }]} />
      <Card><CardContent className="pt-6">
        <ResourceForm
          schema={schema}
          defaultValues={{ payment_date: new Date().toISOString().slice(0, 10), payment_method: "cash" }}
          fields={[
            { name: "client_id", label: "Mijoz", type: "select", required: true, options: clients.map((c) => ({ label: c.name, value: String(c.id) })) },
            { name: "amount", label: "Summa", type: "number", required: true },
            { name: "payment_date", label: "Sana", type: "date", required: true },
            { name: "payment_method", label: "Usul", type: "select", required: true, options: [
              { label: "Naqd", value: "cash" }, { label: "Bank", value: "bank_transfer" },
              { label: "Karta", value: "card" }, { label: "Boshqa", value: "other" },
            ]},
            { name: "reference_number", label: "Referens" },
            { name: "notes", label: "Izoh", type: "textarea" },
          ]}
          loading={mutation.isPending}
          onSubmit={(v) => mutation.mutate(v as never)}
        />
      </CardContent></Card>
    </div>
  );
}
