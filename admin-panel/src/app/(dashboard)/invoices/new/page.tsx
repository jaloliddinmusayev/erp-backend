"use client";

import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";
import { toast } from "sonner";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { ResourceForm } from "@/components/forms/resource-form";
import { listClients } from "@/lib/api/modules/clients";
import { createInvoice } from "@/lib/api/modules/invoices";
import { onMutationError } from "@/lib/api/errors";

const schema = z.object({
  client_id: z.number().min(1),
  invoice_number: z.string().min(1),
  invoice_date: z.string().min(1),
  due_date: z.string().optional(),
  notes: z.string().optional(),
});

export default function NewInvoicePage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data: clients = [] } = useQuery({
    queryKey: ["clients"],
    queryFn: () => listClients({ skip: 0, limit: 200, is_active: true }),
  });

  const mutation = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      createInvoice({ ...body, items: [] }),
    onSuccess: (d) => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      toast.success("Faktura yaratildi (draft)");
      router.push(`/invoices/${d.id}`);
    },
    onError: onMutationError,
  });

  return (
    <div className="space-y-6">
      <PageHeader title="Yangi Invoice" breadcrumbs={[{ label: "Invoices", href: "/invoices" }, { label: "Yangi" }]} />
      <Card><CardContent className="pt-6">
        <ResourceForm
          schema={schema}
          defaultValues={{ invoice_date: new Date().toISOString().slice(0, 10) }}
          fields={[
            { name: "client_id", label: "Mijoz", type: "select", required: true, options: clients.map((c) => ({ label: c.name, value: String(c.id) })) },
            { name: "invoice_number", label: "Raqam", required: true },
            { name: "invoice_date", label: "Sana", type: "date", required: true },
            { name: "due_date", label: "Muddat", type: "date" },
            { name: "notes", label: "Izoh", type: "textarea" },
          ]}
          loading={mutation.isPending}
          onSubmit={(v) => mutation.mutate(v as never)}
        />
      </CardContent></Card>
    </div>
  );
}
