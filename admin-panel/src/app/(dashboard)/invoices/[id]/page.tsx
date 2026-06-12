"use client";

import { use } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ResourceDetailPage } from "@/components/crud/resource-detail-page";
import { invoicesResource } from "@/config/resources/invoices";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { PermissionGuard } from "@/components/crud/permission-guard";
import { formatMoney, formatDate } from "@/lib/utils";
import { issueInvoice, cancelInvoice } from "@/lib/api/modules/invoices";
import { onMutationError } from "@/lib/api/errors";
import { useT } from "@/lib/i18n";
import type { Invoice } from "@/types/api";

export default function InvoiceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const t = useT();
  const { id } = use(params);
  const numId = Number(id);
  const queryClient = useQueryClient();

  const issueMut = useMutation({
    mutationFn: () => issueInvoice(numId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      toast.success(t("toast.invoiceIssued"));
    },
    onError: onMutationError,
  });

  const cancelMut = useMutation({
    mutationFn: () => cancelInvoice(numId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      toast.success(t("toast.invoiceCancelled"));
    },
    onError: onMutationError,
  });

  return (
    <ResourceDetailPage
      config={invoicesResource}
      id={numId}
      getFields={(inv: Invoice) => [
        { label: "fields.number", value: inv.invoice_number },
        { label: "fields.client", value: inv.client?.name },
        { label: "fields.date", value: formatDate(inv.invoice_date) },
        { label: "fields.dueDate", value: formatDate(inv.due_date) },
        { label: "fields.status", value: <StatusBadge status={inv.status} /> },
        { label: "fields.total", value: formatMoney(inv.total_amount) },
        { label: "fields.paidAmount", value: formatMoney(inv.paid_amount) },
        { label: "fields.outstanding", value: formatMoney(inv.outstanding_amount) },
      ]}
      actions={
        <PermissionGuard permission="invoices:write">
          <div className="flex gap-2">
            <Button size="sm" onClick={() => issueMut.mutate(undefined)} disabled={issueMut.isPending}>{t("invoice.issue")}</Button>
            <Button size="sm" variant="destructive" onClick={() => cancelMut.mutate(undefined)} disabled={cancelMut.isPending}>{t("invoice.cancelInvoice")}</Button>
          </div>
        </PermissionGuard>
      }
    />
  );
}
