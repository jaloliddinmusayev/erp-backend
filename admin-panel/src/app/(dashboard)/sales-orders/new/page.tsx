"use client";

import { useRouter } from "next/navigation";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Plus, Trash2 } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { listClients } from "@/lib/api/modules/clients";
import { listProducts } from "@/lib/api/modules/products";
import { createSalesOrder } from "@/lib/api/modules/sales-orders";
import { onMutationError } from "@/lib/api/errors";
import {
  salesOrderCreateSchema,
  type SalesOrderCreateForm,
} from "@/features/sales-orders/schemas";

export default function NewSalesOrderPage() {
  const router = useRouter();
  const { data: clients = [] } = useQuery({
    queryKey: ["clients"],
    queryFn: () => listClients({ skip: 0, limit: 200, is_active: true }),
  });
  const { data: products = [] } = useQuery({
    queryKey: ["products"],
    queryFn: () => listProducts({ skip: 0, limit: 200 }),
  });

  const {
    register,
    control,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<SalesOrderCreateForm>({
    resolver: zodResolver(salesOrderCreateSchema),
    defaultValues: {
      order_date: new Date().toISOString().slice(0, 10),
      items: [{ product_id: 0, ordered_qty: 1, unit_price: 0 }],
    },
  });

  const { fields, append, remove } = useFieldArray({ control, name: "items" });
  const clientId = watch("client_id");

  const mutation = useMutation({
    mutationFn: createSalesOrder,
    onSuccess: (data) => {
      toast.success("Buyurtma yaratildi");
      router.push(`/sales-orders/${data.id}`);
    },
    onError: onMutationError,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Yangi Sales Order"
        breadcrumbs={[
          { label: "Sales Orders", href: "/sales-orders" },
          { label: "Yangi" },
        ]}
      />
      <form onSubmit={handleSubmit((d) => mutation.mutate(d as never))}>
        <Card className="mb-6">
          <CardHeader><CardTitle>Asosiy</CardTitle></CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label>Mijoz *</Label>
              <Select
                value={clientId ? String(clientId) : undefined}
                onValueChange={(v) => setValue("client_id", Number(v))}
              >
                <SelectTrigger className="mt-1.5"><SelectValue placeholder="Tanlang" /></SelectTrigger>
                <SelectContent>
                  {clients.map((c) => (
                    <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.client_id && <p className="text-sm text-destructive">{errors.client_id.message}</p>}
            </div>
            <div>
              <Label>Raqam *</Label>
              <Input className="mt-1.5" {...register("order_number")} />
            </div>
            <div>
              <Label>Sana *</Label>
              <Input type="date" className="mt-1.5" {...register("order_date")} />
            </div>
            <div className="sm:col-span-2">
              <Label>Izoh</Label>
              <Textarea className="mt-1.5" {...register("notes")} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Qatorlar</CardTitle>
            <Button type="button" variant="outline" size="sm" onClick={() => append({ product_id: 0, ordered_qty: 1, unit_price: 0 })}>
              <Plus className="mr-1 h-4 w-4" /> Qator
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            {fields.map((field, index) => (
              <div key={field.id} className="grid gap-3 rounded-lg border p-4 sm:grid-cols-4">
                <div>
                  <Label>Mahsulot</Label>
                  <Select onValueChange={(v) => setValue(`items.${index}.product_id`, Number(v))}>
                    <SelectTrigger className="mt-1"><SelectValue placeholder="Tanlang" /></SelectTrigger>
                    <SelectContent>
                      {products.map((p) => (
                        <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Miqdor</Label>
                  <Input type="number" step="0.01" className="mt-1" {...register(`items.${index}.ordered_qty`, { valueAsNumber: true })} />
                </div>
                <div>
                  <Label>Narx</Label>
                  <Input type="number" step="0.01" className="mt-1" {...register(`items.${index}.unit_price`, { valueAsNumber: true })} />
                </div>
                <div className="flex items-end">
                  <Button type="button" variant="ghost" size="icon" onClick={() => remove(index)} disabled={fields.length === 1}>
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </div>
            ))}
            {errors.items && <p className="text-sm text-destructive">{errors.items.message}</p>}
          </CardContent>
        </Card>

        <Button type="submit" className="mt-6" disabled={mutation.isPending}>
          {mutation.isPending ? "Saqlanmoqda..." : "Yaratish"}
        </Button>
      </form>
    </div>
  );
}
