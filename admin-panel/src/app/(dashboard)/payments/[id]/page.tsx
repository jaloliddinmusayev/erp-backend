"use client";

import { use } from "react";
import { ResourceDetailPage } from "@/components/crud/resource-detail-page";
import { paymentsResource } from "@/config/resources/payments";
import { formatMoney, formatDate } from "@/lib/utils";
import { T } from "@/lib/i18n";
import type { Payment } from "@/types/api";

export default function PaymentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return (
    <ResourceDetailPage
      config={paymentsResource}
      id={Number(id)}
      getFields={(p: Payment) => [
        { label: "fields.client", value: p.client?.name },
        { label: "fields.amount", value: formatMoney(p.amount) },
        { label: "fields.date", value: formatDate(p.payment_date) },
        { label: "fields.method", value: <T k={`paymentMethod.${p.payment_method}`} /> },
        { label: "fields.reference", value: p.reference_number ?? "—" },
        { label: "fields.notes", value: p.notes ?? "—" },
      ]}
    />
  );
}
