"use client";

import { use } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ResourceDetailPage } from "@/components/crud/resource-detail-page";
import { salesOrdersResource } from "@/config/resources/sales-orders";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { PermissionGuard } from "@/components/crud/permission-guard";
import { formatMoney, formatDate } from "@/lib/utils";
import {
  confirmSalesOrder,
  cancelSalesOrder,
  enqueueWms,
} from "@/lib/api/modules/sales-orders";
import { onMutationError } from "@/lib/api/errors";
import type { SalesOrder } from "@/types/api";

export default function SalesOrderDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const numId = Number(id);
  const queryClient = useQueryClient();

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["sales-orders"] });

  const confirmMut = useMutation({
    mutationFn: () => confirmSalesOrder(numId),
    onSuccess: () => { invalidate(); toast.success("Buyurtma tasdiqlandi"); },
    onError: onMutationError,
  });

  const cancelMut = useMutation({
    mutationFn: () => cancelSalesOrder(numId),
    onSuccess: () => { invalidate(); toast.success("Buyurtma bekor qilindi"); },
    onError: onMutationError,
  });

  const wmsMut = useMutation({
    mutationFn: () => enqueueWms(numId),
    onSuccess: () => { invalidate(); toast.success("WMS navbatiga qo'shildi"); },
    onError: onMutationError,
  });

  return (
    <ResourceDetailPage
      config={salesOrdersResource}
      id={numId}
      getFields={(o: SalesOrder) => [
        { label: "Raqam", value: o.order_number },
        { label: "Mijoz", value: o.client?.name },
        { label: "Sana", value: formatDate(o.order_date) },
        { label: "Holat", value: <StatusBadge status={o.status} /> },
        { label: "Fulfillment", value: <StatusBadge status={o.fulfillment_status} /> },
        { label: "Integration", value: <StatusBadge status={o.integration_status} /> },
        { label: "Summa", value: formatMoney(o.total_amount) },
        { label: "WMS ID", value: o.wms_order_id ?? "—" },
        { label: "Izoh", value: o.notes ?? "—" },
      ]}
      actions={
        <PermissionGuard permission="sales_orders:write">
          <div className="flex flex-wrap gap-2">
            <Button size="sm" onClick={() => confirmMut.mutate(undefined)} disabled={confirmMut.isPending}>
              Tasdiqlash
            </Button>
            <Button size="sm" variant="outline" onClick={() => wmsMut.mutate(undefined)} disabled={wmsMut.isPending}>
              WMS ga yuborish
            </Button>
            <Button size="sm" variant="destructive" onClick={() => cancelMut.mutate(undefined)} disabled={cancelMut.isPending}>
              Bekor qilish
            </Button>
          </div>
        </PermissionGuard>
      }
    />
  );
}
